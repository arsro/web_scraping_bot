# web_scraping_bot

- build docker 
`docker build -t web_scraping_bot .`

- enter docker
`docker run -i -t --rm --name scraping_bot -v {work_pass}:/src/sandbox web_scraping_bot /bin/bash`

- run only
`docker run --rm --name scraping_bot -v {work_pass}:/src/sandbox web_scraping_bot`