'use strict';

const { app, BrowserWindow } = require('electron');
const url = require('url');
const path = require('path');
const tree_kill = require('tree-kill');
const find_process = require('find-process');
const psList = require('ps-list');
const PY_DIST_FOLDER = 'dist';
const EXEC_NAME = 'OnionMessengerServer'

let mainWindow;
var pid;


const isNotPackaged = () => {
    const fullPath = path.join(__dirname, 'src')
    return require('fs').existsSync(fullPath)
}

function getExecNameWithExtension() {
    if (process.platform === 'win32') {
        return EXEC_NAME + '.exe';
    }
}

function getServerExecPath() {
    if (isNotPackaged()) {
        return path.join(__dirname, PY_DIST_FOLDER, getExecNameWithExtension());
    } else {
        return path.join(process.resourcesPath, 'app', PY_DIST_FOLDER, getExecNameWithExtension());
    }
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1024,
        height: 768,
        show: false,
        webPreferences: {
            nodeIntegration: true
        }
    });
    mainWindow.maximize();
    mainWindow.show();

    mainWindow.loadURL(
        url.format({
            pathname: path.join(__dirname, PY_DIST_FOLDER, 'angular-client', 'index.html'),
            protocol: 'file:',
            slashes: true
        })
    );
    var executablePath = getServerExecPath();
    var child = require('child_process').spawn(executablePath);

    child.stderr.on('data', function(data) {
        console.log('stderr: ' + data);
    });

    child.stdout.on('data', function(data) {
        console.log('stdout: ' + data);
    });

    mainWindow.on('closed', function () {
        mainWindow = null;
    });
}

app.on('ready', createWindow);

app.on('window-all-closed', async () => {
    const procs = await psList();

    if (process.platform !== 'darwin')
        app.quit();

    procs.filter(function (proc) {
        return proc.name === getExecNameWithExtension();
    })
    .forEach(item => {
        tree_kill(item.pid);
    });
});

app.on('before-quit', function() {
    app.removeAllListeners('close');
});

app.on('activate', function () {
    if (mainWindow === null)
        createWindow()
});