IGNORE_CHANNELS = os.getenv('IGNORE_CHANNELS')

class Common:
    def metodo_comun(self):
        print("Este es un método común")

    async def GetDeathCount(ctx, player):
        deathcount = 0
        logs = list()
        for root, dirs, files in os.walk(LOG_PATH):
            for f in files:
                if "_user.txt" in f:
                    lpath = os.path.join(root,f)
                    logs.append(lpath)
        for log in logs:
            with open(log, 'r') as file:
                for line in file:
                    if player.lower() in line.lower():
                        if "died" in line:
                            deathcount += 1

        t = await lookuptime(ctx, player)
        return f"{player} has died {deathcount} times. Playtime: {t}"

    async def pretty_time_delta(seconds):
        sign_string = '-' if seconds < 0 else ''
        seconds = abs(int(seconds))
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        if days > 0:
            return '%s%dd, %dh, %dm, %ds' % (sign_string, days, hours, minutes, seconds)
        elif hours > 0:
            return '%s%dh, %dm, %ds' % (sign_string, hours, minutes, seconds)
        elif minutes > 0:
            return '%s%dm, %ds' % (sign_string, minutes, seconds)
        else:
            return '%s%ds' % (sign_string, seconds)

    async def getallplaytime(ctx):
        logs = list()
        user_time = {}
        for root, dirs, files in os.walk(LOG_PATH):
            for f in files:
                if "_user.txt" in f:
                    lpath = os.path.join(root,f)
                    logs.append(lpath)
        connect_time = {}
        fc_last_date = {}
        dc_last_date = {}
        for log in logs:
            with open(log, 'r') as file:
                for line in file:
                    if "fully connected" in line:
                        c_sl = line.split()
                        c_username = c_sl[3].strip('"')
                        c_etime = " ".join(c_sl[:2]).strip("[]")
                        c_dt = datetime.strptime(c_etime, '%d-%m-%y %H:%M:%S.%f')
                        connect_time[c_username] = c_dt
                        if fc_last_date.get(c_username, datetime.min) < c_dt:
                            fc_last_date[c_username] = c_dt

                    if "removed connection" in line:
                        r_sl = line.split()
                        r_username = r_sl[3].strip('"')
                        r_etime = " ".join(r_sl[:2]).strip("[]")
                        r_dt = datetime.strptime(r_etime, '%d-%m-%y %H:%M:%S.%f')
                        if r_username in connect_time:
                            time_segment = r_dt - connect_time[r_username]
                            time_segment = time_segment
                            if r_username not in user_time.keys():
                                user_time[r_username] = time_segment
                            else:
                                user_time[r_username] = time_segment + user_time[r_username]
                            del connect_time[r_username]
                        if dc_last_date.get(r_username, datetime.min) < r_dt:
                            dc_last_date[r_username] = r_dt

        for user in dc_last_date:
            if user in fc_last_date:
                if dc_last_date[user] < fc_last_date[user]:
                    user_time[user] = user_time[user] + (datetime.now() - fc_last_date[user])
                    print(f"User {user} probably still connected")
                    u = user + "(active)"
                    user_time[u] = user_time[user]
                    del user_time[user]
        user_time = dict(reversed(sorted(user_time.items(), key=lambda item: item[1])))
        for user in user_time:
            time_pretty = await pretty_time_delta(user_time[user].total_seconds())
            user_time[user] = time_pretty
        return user_time


    async def lookuptime(ctx, username):
        pl = await getallplaytime(ctx)
        for user in pl:
            if username == user.replace("(active)",""):
                return pl[user]

    async def getalldeaths(ctx):
        deathcount = 0
        logs = list()
        deathdict = {}
        for root, dirs, files in os.walk(LOG_PATH):
            for f in files:
                if "_user.txt" in f:
                    lpath = os.path.join(root,f)
                    logs.append(lpath)
        for log in logs:
            with open(log, 'r') as file:
                for line in file:
                    if "died at (" in line:
                        player = line.split()[3]
                        if player in deathdict:
                            deathdict[player] += 1
                        else:
                            deathdict[player] = 1
        rstring = ""
        deathdict = dict(reversed(sorted(deathdict.items(), key=lambda item: item[1])))
        for x in deathdict:
            p = x
            c = deathdict[x]
            t = await lookuptime(ctx, p)
            rstring += f"{p} has died {c} times. Playtime: {t}\n"
        return rstring


    async def getmods():
        modlist = list()
        with open(os.path.join(os.path.split(LOG_PATH)[0],"Server","servertest.ini"), 'r') as file:
            for line in file:
                if "Mods=" in line:
                    mods_split = line.split("=")
                    if len(mods_split) > 1:
                        mods_list_split = mods_split[1].split(';')
                        for mod in mods_list_split:
                            modlist.append(mod)
        return "\n".join(modlist)


    async def lookupsteamid(name):
        for root, dirs, files in os.walk(LOG_PATH):
            for f in files:
                if "_user.txt" in f:
                    lpath = os.path.join(root,f) 
                    with open(lpath, 'r') as file:
                        for line in file:
                            if "fully connected" in line:
                                if name in line:
                                    return line.split()[2]
        
    async def IsAdmin(ctx):
        is_present = [i for i in ctx.author.roles if i.name in ADMIN_ROLES]
        return is_present

    async def IsMod(ctx):
        is_present = [i for i in ctx.author.roles if i.name in MODERATOR_ROLES]
        return is_present

    async def IsServerRunning():
        for proc in psutil.process_iter():
            lname = proc.name().lower()
            if "projectzomboid" in lname:
            return True
        return False

    async def restart_server(ctx):
        await ctx.send("Shutting server down, please wait...")
        await rcon_command(ctx,[f"save"])
        co = check_output(RESTART_CMD, shell=True)
        await ctx.send(f"Server restarted, it may take a minute to be fully ready")
        server_down = False
        while not server_down:
            d = await rcon_command(ctx, [f"players"])
            if "refused" in d:
                server_down = True
            await asyncio.sleep(5)
        
        if os.name == 'nt':
            terminate_zom = '''wmic PROCESS where "name like '%java.exe%' AND CommandLine like '%zomboid.steam%'" Call Terminate'''
            terminate_shell = '''wmic PROCESS where "name like '%cmd.exe%' AND CommandLine like '%StartServer64.bat%'" Call Terminate'''
            check_output(terminate_zom, shell=True)
            check_output(terminate_shell, shell=True)
            server_start = [os.path.join(SERVER_PATH,"StartServer64.bat")]
            p = Popen(server_start, creationflags=subprocess.CREATE_NEW_CONSOLE)
            r = p.stdout.read()
            r = r.decode("utf-8")
        else:
            check_output(RESTART_CMD, shell=True)

        await ctx.send("Server restarted, it may take a minute to be fully ready")

    async def rcon_command(ctx, command):
        try:
            sr = SourceRcon(RCONSERVER, int(RCONPORT), RCONPASS)
            r = sr.rcon(" ".join(command))
            return r.decode('utf-8')
        except Exception as e:
            print(e)

    async def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]


    async def IsChannelAllowed(ctx):
        channel_name = str(ctx.message.channel)
        is_present = [i for i in IGNORE_CHANNELS if i.lower() == channel_name.lower()]
        if channel_name in IGNORE_CHANNELS:
            if channel_name not in block_notified:
                await ctx.send("Not allowed to run commands in this channel")
                block_notified.append(channel_name)
            raise Exception("Not allowed to operate in channel")
        
    async def pzplayers():
        plist = list()
        c_run = ""
        c_run = await rcon_command(None, ["players"])
        c_run = c_run.split('\n')[1:-1]
        return len(c_run)

    async def status_task():
        while True:
            _serverUp = await IsServerRunning()
            if _serverUp:
                playercount = 0
                try:
                    playercount = await pzplayers()
                except Exception as e:
                    print(e)
                    await asyncio.sleep(20)
                    continue
                
                await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{playercount} survivors online"))
            else:
                await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"Server offline"))
            await asyncio.sleep(20)    