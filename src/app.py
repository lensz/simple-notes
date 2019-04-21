import os
import time

from bottle import route, post, run, request, static_file, template, TEMPLATE_PATH

from utils import createDirsIfNecessary, hashOfFile

currentModulePath = os.path.dirname(os.path.realpath(__file__))

NOTE_PORT = os.getenv("SIMPE_NOTES_PORT", 63636)
NOTE_FOLDER_PATH = os.getenv("SIMPE_NOTES_NOTE_FOLDER_PATH", "./default_notes_location")

NOTE_OVERWRITE_PROTECTION_SUFFIX = ".alt"
TEMPLATE_DIRECTORY = os.path.join(currentModulePath, "templates")
STATIC_FILES_DIRECTORY = os.path.join(currentModulePath, "static")

@route("/static/<filepath:path>")
def server_static(filepath):
    return static_file(filepath, root=STATIC_FILES_DIRECTORY)

@post("/writeNote")
def writeNote():
    notename = request.json["noteName"]
    notetext = request.json["noteText"]
    rememberedNotehash = request.json["noteHash"]
    notepath = NOTE_FOLDER_PATH + "/" + notename
    notedir = "/".join(notepath.split("/")[0:-1])
    createDirsIfNecessary(notedir)

    if os.path.exists(notepath):
        currentNoteHash = hashOfFile(notepath)
        if rememberedNotehash != currentNoteHash:
            notename += NOTE_OVERWRITE_PROTECTION_SUFFIX
            notepath += NOTE_OVERWRITE_PROTECTION_SUFFIX
    try:
        with open(notepath, "w") as note:
            note.write(str(notetext))
    except IOError as e:
        return HTTPResponse(status=500, body="IO Error during note creation")
    return {
        "createdNote": notename
    }

@route("/")
@route("/list")
def notelist():
    createDirsIfNecessary(NOTE_FOLDER_PATH)
    return template("note-list", notelist=sorted(getListOfNotePaths()))

def getListOfNotePaths():
    listOfFiles = []
    for (dirpath, dirnames, filenames) in os.walk(NOTE_FOLDER_PATH):
        dirPathWithoutNotesFolder = dirpath[len(NOTE_FOLDER_PATH) + 1:]
        if dirPathWithoutNotesFolder.startswith("."):
            continue
        for filename in filenames:
            if filename.startswith("."):
                continue
            path = os.path.join(dirPathWithoutNotesFolder, filename)
            listOfFiles.append(path)
    return listOfFiles

@route("/<notename:path>")
def viewNote(notename):
    createDirsIfNecessary(NOTE_FOLDER_PATH)

    notepath = NOTE_FOLDER_PATH + "/" + notename
    try:
        notehash = hashOfFile(notepath)
    except IOError as e:
        notehash = "new note"


    noteText = ""
    noteLastModificationDate = "new note"
    if os.path.isfile(notepath):
        noteLastModificationDate = time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(os.path.getmtime(notepath)))
        with open(notepath, "r") as note:
            noteText += note.read()

    return template("note-detail", notename=notename, notehash=notehash, noteLastModificationDate=noteLastModificationDate, notetext=noteText)

TEMPLATE_PATH.insert(0, TEMPLATE_DIRECTORY)
run(server="gunicorn", host="0.0.0.0", port=NOTE_PORT)
