'''


FOR SOME REASON THIS SCRIPT DOESN'T OUTPUT ANYTHING
ON SUBLIME TEXT, BUT IT DOES OUTPUT ON VS CODE AND
THE WINDOWS COMMAND LINE, PERHAPS THIS "PROBLEM"
ONLY OCCURS IN MY COMPUTER, BUT WHO KNOWS...


'''


import re
import urllib.request
import time
import os
import shutil
import requests
from bs4 import BeautifulSoup


#Progress bar from https://stackoverflow.com/a/34325723
# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

clear = lambda: os.system('cls' if os.name == 'nt' else 'clear') # Clear screen (NT is Windows) 


url = 'https://webtoons.com'

cartoons = ['/en/fantasy/the-fever-king/list?title_no=1659'] # URLs to cartoon's homepage
cartoons_names = [] # List containing titles of cartoons acquired from requested URLs

for cartoon in cartoons:
    cartoon=cartoon.split("/")
    cartoons_names.append(cartoon[3].replace("-", " ").title())



current_index = 0

os.mkdir('Webtoons')
for cartoon in cartoons:
    if not os.path.isdir(f'Webtoons/{cartoons_names[current_index]}'): # Create folder for the cartoon if it doesn't exist
        os.mkdir(f'Webtoons/{cartoons_names[current_index]}')

    final_page = cartoon + '&page=999999'
    base_page = requests.get(url+final_page, headers={'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3724.8 Safari/537.36'}, cookies={'locale':'en', 'needGDPR':'false', 'needCCPA':'false', 'needCOPPA':'false'}).text
    base_page_source = BeautifulSoup(base_page, 'lxml')

    last_page = base_page_source.find('div', {'class': 'paginate'})

    last_page = last_page.find('a', {'onclick': 'return false;'})

    last_page = int(last_page.find('span').text) # Finds how many pages there are for the title

    episodes = []
    clear()
    for page in range(1, last_page+1): # Goes through each page and finds the links to each of the episodes
        printProgressBar(page, last_page+1, prefix = 'Loading Episodes')

        base_page = requests.get(url+cartoon+f'&page={page}', headers={'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3724.8 Safari/537.36'}).text
        base_page_source = BeautifulSoup(base_page, 'lxml')
        all_episodes = base_page_source.find('ul', id='_listUl')
        all_episodes = all_episodes.findAll('li')
        old_episodes = []
        for episode in all_episodes:
            #print(episode.find('a'))
            #print('DON')
            old_episodes.append(episode.find('a'))
        for episode in old_episodes:
            #print(episode['href'])
            #print("ok")
            episodes.append(episode['href'])

    episodes = episodes[::-1] # Stores all the links for the episodes in a list

    current_episode = 1
    clear()
    for episode in episodes: # Goes through each of the episodes, create a folder for each of them (if it doesn't exist), finds the links to all the cartoon's images in the page
        #print(f'Current episode: {cartoons_names[current_index]} - {episode}')
        printProgressBar(episodes.index(episode), len(episodes), prefix = 'Total Progress')
        if not os.path.isdir(f'Webtoons/{cartoons_names[current_index]}/episode-{current_episode}'):
            os.mkdir(f'Webtoons/{cartoons_names[current_index]}/episode-{current_episode}')

        current_episode_page = requests.get(episode, headers={'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3724.8 Safari/537.36'}).text

        current_episode_source = BeautifulSoup(current_episode_page, 'lxml')

        image_div = current_episode_source.find('div', id='_imageList')

        images = image_div.findAll('img', {'alt': 'image', 'class': '_images'})

        image_count = 0

        for image in images: # For each image link found in the episode, store it inside the current episode's folder as .jpg (if it doesn't already exist)
            #print(image)
            if images.index(image) == 0:
                print()
            printProgressBar(images.index(image), len(images), prefix = 'Current Episode')
            if not os.path.isfile(f'Webtoons/{cartoons_names[current_index]}/episode-{current_episode}/{image_count}.jpg'):
                r = urllib.request.Request(image['data-url'], headers={'Referer': 'https://webtoons.com/'})
                response = urllib.request.urlopen(r)
                with open(f'Webtoons/{cartoons_names[current_index]}/episode-{current_episode}/{image_count}.jpg', 'wb') as f:
                    shutil.copyfileobj(response, f)
                image_count += 1
            else:
                image_count += 1
                pass
        with open(f'Webtoons/{cartoons_names[current_index]}/episode-{current_episode}/num_images.txt', 'w') as file:
            file.write(str(image_count - 1)) # Stores how many images are in the episode inside a text file, which will be used as a reference by the fetch api to load the images inside the index.html
        with open(f'Webtoons/{cartoons_names[current_index]}/episode-{current_episode}/index.html', 'w') as index:
            index.write(r'''

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>COMIQS!</title>
</head>
<body>
<style>
html, body {
    background-color: black;
    height: 100%;
}

.container {
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.images {
    width: auto;
    height: auto;
}
</style>

<div class="container">
</div>

<script>
    "use strict";
    let container = document.querySelector('.container');

    fetch('num_images.txt').then(response => response.text()).then(
       function(data) {
           const images = parseInt(data);
           let img = 1;
           setTimeout(function () {
                   while (img < images) {
                       let new_img = container.appendChild(document.createElement('img'));
                       new_img.className = 'images';
                       new_img.setAttribute('src', './' + img + '.jpg');
                       img++;
                   }
               }, 0)
        }

    );
</script>
</body>
</html>

            ''') # Creates an index.html file to mimic Webtoon's style of displaying the cartoons (one image below another), with a black background, because white hurts the eyes much more than black, and is less comfortable to look at
        with open(f'Webtoons/{cartoons_names[current_index]}/episode-{current_episode}/run-server.bat', 'w') as faiol:
            faiol.write('python -m http.server') # Starts a local server, which is needed to load the images, using the fetch api
        current_episode += 1
    current_index += 1
