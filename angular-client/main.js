'use strict';

const { app, BrowserWindow } = require('electron')
const url = require("url");
const path = require("path")
const tree_kill = require("tree-kill");

let mainWindow;
var pid;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        show: false,
        webPreferences: {
            nodeIntegration: true
        }
    });
    mainWindow.maximize();
    mainWindow.show();

    mainWindow.loadURL(
        url.format({
            pathname: path.join(__dirname, `/dist/angular-client/index.html`),
            protocol: "file:",
            slashes: true
        })
    );

    var executablePath = '../appbuild/dist/OnionMessenger.exe';
    var child = require('child_process').spawn(executablePath);
    pid = child.pid;
    mainWindow.on('closed', function () {
        mainWindow = null
        tree_kill(pid);
    });
}

app.on('ready', createWindow);

app.on('window-all-closed', function () {
    if (process.platform !== 'darwin')
        app.quit()
});

app.on('activate', function () {
    if (mainWindow === null)
        createWindow()
});

app.on('quit', function () {
    tree_kill(pid);
});

app.once('before-quit', () => {
    mainWindow.removeAllListeners('close');
}); 