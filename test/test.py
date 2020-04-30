import glob
import os

import asyncio


async def hello(test):
    for i in range(test):
        print(i)


async def main():
    await hello(10)


if __name__ == '__main__':
    asyncio.run(main())


def async():
    print()
