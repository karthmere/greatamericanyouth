const express = require('express');
const isbot = require('isbot');
const sqlite = require('sqlite3');
const path = require('path');
const ejs = require('ejs');
const compression = require('compression')

let metadataCache = new Map();


const app = express();
app.use(compression())
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, '/client/dist/greatamericanyouth'));
const db = new sqlite.Database('greatamericanyouth.db');

const PORT = 4000;

app.use(express.static(__dirname + '/client/dist/greatamericanyouth'));

app.get('*', (req, res) => {
    const index = path.join(__dirname, '/client/dist/greatamericanyouth/index.ejs');
    const hostUrl = 'https://' + req.get('Host');
    const urlPath = req.originalUrl;
    const urlArray = urlPath.split("/");
    const urlName = urlArray[urlArray.length - 1];
    let metadata = {
        title: "Great American Youth",
        description: "Daily news at your will, obedient, submissive",
        thumbnail: "",
        url: "https://greatamericanyouth.com"
    }
    if (req.originalUrl.includes("news")) {
        if (metadataCache.has(urlName)) {
            metadata = metadataCache.get(urlName);
            res.render(index,
                metadata);
        }
        else {
            db.get('SELECT * FROM Articles WHERE urlName = ?', [urlName], (err, row) => {
                if (row) {
                    metadata = {
                        title: row["title"],
                        description: row["description"],
                        thumbnail: hostUrl + '/' + row["thumbnail"],
                        url: hostUrl + urlPath
                    };
                    metadataCache.set(urlName, metadata);
                }
                res.render(index,
                    metadata);
            });
        }
    }
    else {
        res.render(index, metadata);
    }
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
