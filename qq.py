import queue
import threading
import time
from web_driver import WebDriver
import  concurrent.futures

class ScraperCategory(WebDriver):
    def __init__(self, url):
        self.url = url
        super().__init__(url)

class MultiThread(threading.Thread,WebDriver):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        print(f"{threading.current_thread().name}")
        process_queue()

# Process thr queue
def process_queue():
    while True:
        try:
            site = category_que.get(block=False)
        except queue.Empty:
            return
        else:
            get_web(site)
            time.sleep(2)

def get_web(site):
    site_link=ScraperCategory(site)
    site_link.driver.get(site_link.url)
    print(f"{threading.current_thread().name}      {site_link.driver.title}")
    site_link.driver.quit()



input_values = [
                'https://w3schools.com',
                'https://google.com',
                'https://facebook.com',
                'https://github.com',
                'https://youtube.com',
                'https://apple.com',
                'https://en.wikipedia.org',
                'https://docs.google.com',
                'https://mozilla.org',
                'https://cloudflare.com',
                'https://twitter.com'
                ]
                
start = time.perf_counter()
with concurrent.futures.ThreadPoolExecutor(max_workers= 3, thread_name_prefix='Fetching_URL') as executor:
    futures = [executor.submit(get_web, datum) for datum in input_values]
    for future in concurrent.futures.as_completed(futures):
        if future.result():
            print(f"{threading.current_thread().name}) -{future.result()}")
final = time.perf_counter()
# # fill the queue
# category_que = queue.Queue()
# for x in input_values:
#     category_que.put(x)
# # initializing and starting 3 threads
# thread1 = MultiThread('First')
# thread2 = MultiThread('Second')
# thread3 = MultiThread('Third')


# # Start the threads
# thread1.start()
# thread2.start()
# thread3.start()



# # Join the threads
# thread1.join()
# thread2.join()
# thread3.join()
# final = time.perf_counter()
print(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds to  fetch ")
# {len(DataParserClass.data)} items URL")
