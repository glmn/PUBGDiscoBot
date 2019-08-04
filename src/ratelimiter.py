import time
import asyncio

class RateLimiter:

  def __init__(self, rate, per):
    self.rate = rate
    self.per = per
    self.allowance = rate
    self.lastCheck = time.time()

  async def wait(self):
    current = time.time()
    timePassed = current - self.lastCheck
    self.lastCheck = current
    self.allowance += timePassed * (self.rate / self.per)
    print(self.allowance)
    if self.allowance > self.rate:
      self.allowance = self.rate
    if self.allowance < 1.0:
      print('wait')
      timeToSleep = (1 - self.allowance) * (self.per / self.rate)
      self.lastCheck = time.time() + timeToSleep
      self.allowance = 0.0
      await asyncio.sleep(timeToSleep)
    else:
      self.allowance -= 1.0
    
    return True
