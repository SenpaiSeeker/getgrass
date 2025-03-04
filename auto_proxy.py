class ProxyChecker(__import__("nsdev").LoggerHandler):
    def __init__(self):
        super().__init__()
        self.asyncio = __import__("asyncio")
        self.datetime = __import__("datetime")
        self.pytz = __import__("pytz")
        self.sys = __import__("sys")
        self.os = __import__("os")
        self.aiohttp = __import__("aiohttp")

        self.PROXY_URLS = ["https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt"]
        self.SEMAPHORE_LIMIT = 100

    async def fetch_proxies(self, url):
        async with self.aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        proxies = (await response.text()).strip().splitlines()
                        self.info(f"Fetched {len(proxies)} proxies from {url}.")
                        return proxies
                    else:
                        self.error(f"Failed to fetch proxies from {url}. Status code: {response.status}.")
            except (self.aiohttp.ClientError, self.asyncio.TimeoutError) as e:
                self.error(f"Error fetching proxies from {url}: {e}")
        return []

    async def check_proxy(self, proxy):
        test_url = "http://httpbin.org/ip"
        if not proxy.startswith("http://") and not proxy.startswith("https://"):
            self.error(f"Invalid proxy format: {proxy}")
            return None

        async with self.aiohttp.ClientSession() as session:
            try:
                async with session.get(test_url, proxy=proxy, timeout=15) as response:
                    if response.status == 200:
                        self.info(f"Proxy {proxy} is working.")
                        return proxy
                    else:
                        self.error(f"Proxy {proxy} failed with status code: {response.status}.")
            except (self.aiohttp.ClientError, self.asyncio.TimeoutError) as e:
                self.error(f"Proxy {proxy} is not working: {e}")
        return None

    async def save_valid_proxies(self, proxies, proxy_file):
        semaphore = self.asyncio.Semaphore(self.SEMAPHORE_LIMIT)

        async def limited_check_proxy(proxy):
            async with semaphore:
                return await self.check_proxy(proxy)

        tasks = [self.asyncio.create_task(limited_check_proxy(proxy)) for proxy in proxies]
        valid_proxies = []

        for i in range(0, len(tasks), 50):
            batch = tasks[i : i + 50]
            results = await self.asyncio.gather(*batch)
            valid_proxies.extend([proxy for proxy in results if proxy])

        with open(proxy_file, "w") as file:
            file.write("\n".join(valid_proxies))

        self.info(f"Saved {len(valid_proxies)} valid proxies to {proxy_file}.")

    async def process_proxies(self, proxy_file):
        self.os.system("clear" if self.os.name == "posix" else "cls")
        self.info("Starting to fetch and validate proxies...")

        all_proxies = []
        for url in self.PROXY_URLS:
            all_proxies.extend(await self.fetch_proxies(url))

        self.info(f"Validating {len(all_proxies)} proxies...")
        await self.save_valid_proxies(all_proxies, proxy_file)

    def _run(self, proxy_file):
        self.asyncio.run(self.process_proxies(proxy_file))
