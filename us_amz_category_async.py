#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import aiohttp
import requests
import traceback
from bs4 import BeautifulSoup
from bs4.element import Tag
from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Sequence
from sqlalchemy.orm import sessionmaker, scoped_session
root_list = ['https://www.amazon.com/Best-Sellers/zgbs/amazon-devices',
 'https://www.amazon.com/Best-Sellers-Amazon-Launchpad/zgbs/boost',
 'https://www.amazon.com/Best-Sellers-Appliances/zgbs/appliances',
 'https://www.amazon.com/Best-Sellers-Appstore-Android/zgbs/mobile-apps',
 'https://www.amazon.com/Best-Sellers-Arts-Crafts-Sewing/zgbs/arts-crafts',
 'https://www.amazon.com/Best-Sellers-Automotive/zgbs/automotive',
 'https://www.amazon.com/Best-Sellers-Baby/zgbs/baby-products',
 'https://www.amazon.com/Best-Sellers-Beauty/zgbs/beauty',
 'https://www.amazon.com/best-sellers-books-Amazon/zgbs/books',
 'https://www.amazon.com/best-sellers-music-albums/zgbs/music',
 'https://www.amazon.com/best-sellers-camera-photo/zgbs/photo',
 'https://www.amazon.com/Best-Sellers-Cell-Phones-Accessories/zgbs/wireless',
 'https://www.amazon.com/Best-Sellers/zgbs/fashion',
 'https://www.amazon.com/Best-Sellers-Collectible-Coins/zgbs/coins',
 'https://www.amazon.com/Best-Sellers-Computers-Accessories/zgbs/pc',
 'https://www.amazon.com/Best-Sellers-MP3-Downloads/zgbs/dmusic',
 'https://www.amazon.com/Best-Sellers-Electronics/zgbs/electronics',
 'https://www.amazon.com/Best-Sellers-Entertainment-Collectibles/zgbs/entertainment-collectibles',
 'https://www.amazon.com/Best-Sellers-Gift-Cards/zgbs/gift-cards',
 'https://www.amazon.com/Best-Sellers-Grocery-Gourmet-Food/zgbs/grocery',
 'https://www.amazon.com/Best-Sellers-Handmade/zgbs/handmade',
 'https://www.amazon.com/Best-Sellers-Health-Personal-Care/zgbs/hpc',
 'https://www.amazon.com/Best-Sellers-Home-Kitchen/zgbs/home-garden',
 'https://www.amazon.com/Best-Sellers-Industrial-Scientific/zgbs/industrial',
 'https://www.amazon.com/Best-Sellers-Kindle-Store/zgbs/digital-text',
 'https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen',
 'https://www.amazon.com/Best-Sellers-Magazines/zgbs/magazines',
 'https://www.amazon.com/best-sellers-movies-TV-DVD-Blu-ray/zgbs/movies-tv',
 'https://www.amazon.com/Best-Sellers-Musical-Instruments/zgbs/musical-instruments',
 'https://www.amazon.com/Best-Sellers-Office-Products/zgbs/office-products',
 'https://www.amazon.com/Best-Sellers-Garden-Outdoor/zgbs/lawn-garden',
 'https://www.amazon.com/Best-Sellers-Pet-Supplies/zgbs/pet-supplies',
 'https://www.amazon.com/Best-Sellers-Prime-Pantry/zgbs/pantry',
 'https://www.amazon.com/best-sellers-software/zgbs/software',
 'https://www.amazon.com/Best-Sellers-Sports-Outdoors/zgbs/sporting-goods',
 'https://www.amazon.com/Best-Sellers-Sports-Collectibles/zgbs/sports-collectibles',
 'https://www.amazon.com/Best-Sellers-Home-Improvement/zgbs/hi',
 'https://www.amazon.com/Best-Sellers-Toys-Games/zgbs/toys-and-games',
 'https://www.amazon.com/best-sellers-video-games/zgbs/videogames']


Base = declarative_base()
engine = create_engine('postgresql://postgres:password@localhost:5432/amz', client_encoding='utf8')
Session = scoped_session(sessionmaker(engine))
class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, Sequence('category_id_seq'), primary_key=True)
    link = Column(String)
    name = Column(String)
Base.metadata.create_all(engine)

async def crawl(url, current_category, session, db):
    db.add(Category(link=url, name=current_category))
    db.commit()
    async with session.get(url) as r:
        result = await r.text(encoding='utf-8')
        soup = BeautifulSoup(result, features="lxml")
        span = soup.find(name='span', attrs={'class': 'zg_selected'})

        # 递归爬
        parent = span.parent.parent
        print(url, current_category)
        if parent.ul:
            ul = parent.ul
            for li in filter(lambda x: isinstance(x, Tag), ul):
                while True:
                    try:
                        await crawl(li.a['href'],
                                    current_category=current_category+'<'+str(li.string),
                                    session=session,
                                    db=db)
                        break
                    except Exception:
                        print(traceback.print_exc())


async def main():
    db = Session()
    async with aiohttp.ClientSession() as session:
        for url in root_list:
            res = requests.get(url).text
            soup = BeautifulSoup(res, 'html.parser')
            span = soup.find(name='span', attrs={'class': 'zg_selected'})
            if span:
                string = str(span.string)
                await crawl(
                      url,
                      current_category='Any Department'+'<'+string,
                      session=session,
                      db=db
                )

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        main()
    )
    loop.close()

    print('\n\nALL DONE!!!\n\n')
