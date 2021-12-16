#!/usr/bin/env python
import curses
import can
import sys
import threading
import time


bustype = 'socketcan'
run = True

class BottomMenu():
    def __init__(self, assigned_window, tui):
        self.window = assigned_window
        self.tui = tui
        self.tui.lock.acquire()
        self.window.addstr("F5", curses.color_pair(TUI.COLOR_MENU_SHORTCUT))
        self.window.addstr("Redraw", curses.color_pair(TUI.COLOR_MENU_DESC))
        self.window.addstr("F6", curses.color_pair(TUI.COLOR_MENU_SHORTCUT))
        self.window.addstr("SortBy", curses.color_pair(TUI.COLOR_MENU_DESC))
        self.window.addstr("F8", curses.color_pair(TUI.COLOR_MENU_SHORTCUT))
        self.window.addstr("Clear", curses.color_pair(TUI.COLOR_MENU_DESC))
        self.window.addstr("F10", curses.color_pair(TUI.COLOR_MENU_SHORTCUT))
        self.window.addstr("Quit", curses.color_pair(TUI.COLOR_MENU_DESC))
        self.drawn = False
        self.tui.lock.release()

    def redraw(self):
        if not self.drawn:
            self.tui.lock.acquire()
            self.window.refresh()
            self.drawn = True
            self.tui.lock.release()

class MessagesHeader():
    def __init__(self, assigned_window, tui):
        self.window = assigned_window
        self.drawn = False
        self.tui = tui
        self.sort = None
        self.sortAscending = False

    def redraw(self):
        if not self.drawn:
            self.tui.lock.acquire()
            self.window.bkgd(' ', curses.color_pair(TUI.COLOR_HEADER))
            for col in self.tui.visibleColumns:
                text = self.tui.getColumnDescription(col)
                if self.sort == col:
                    if self.sortAscending:
                        text = "^" + text
                    else:
                        text = "v" + text
                else:
                    text = " " + text
                offset = self.tui.getColumnOffset(col)
                if (offset > 0):
                    offset -= 1
                self.window.addstr(0, offset, text, curses.color_pair(TUI.COLOR_HEADER))

            self.window.refresh()
            self.drawn = True
            self.tui.lock.release()

    def setSort(self, column, ascending):
        self.drawn = False
        self.sort = column
        self.sortAscending = ascending
        self.redraw()

class MessagesPad():
    def __init__(self, assigned_window, x, y, maxX, maxY, tui):
        self.window = assigned_window
        self.x = x
        self.y = y
        self.maxX = maxX
        self.maxY = maxY
        self.yOffset = 0
        self.tui = tui
        self.messages = [ ]
        self.counts = { }
        self.changes = { }
        self.hilights = { }
        self.sort = None
        self.sortAscending = False
        self.lastMessage = None

    def redraw(self):
        i = 0
        for msg in self.messages:
            for col in self.tui.visibleColumns:
                if msg.arbitration_id == self.lastMessage.arbitration_id and col in self.hilights[self.lastMessage.arbitration_id]:
                    self.window.addstr(i, self.tui.getColumnOffset(col), str(self.getColumnForMessage(msg, col)), curses.color_pair(TUI.COLOR_MSG_HILIGHT))
                elif col in self.hilights[msg.arbitration_id]:
                   self.window.addstr(i, self.tui.getColumnOffset(col), str(self.getColumnForMessage(msg, col)), curses.color_pair(TUI.COLOR_MSG_HILIGHT_OLD))
                else:
                   self.window.addstr(i, self.tui.getColumnOffset(col), str(self.getColumnForMessage(msg, col)), curses.color_pair(TUI.COLOR_MSG))
            i += 1

        self.window.refresh(self.yOffset, 0, self.x,self.y, self.maxX, self.maxY)


    def getColumnForMessage(self, message, column):
        if column is TUI.COLUMN_TIMESTAMP:
            return message.timestamp
        elif column is TUI.COLUMN_MSGID:
            return f'{message.arbitration_id:03x}'
        elif column is TUI.COLUMN_BODY_BYTE_0:
            return f'{message.data[0]:02x}'
        elif column is TUI.COLUMN_BODY_BYTE_1:
            return f'{message.data[1]:02x}'
        elif column is TUI.COLUMN_BODY_BYTE_2:
            return f'{message.data[2]:02x}'
        elif column is TUI.COLUMN_BODY_BYTE_3:
            return f'{message.data[3]:02x}'
        elif column is TUI.COLUMN_BODY_BYTE_4:
             return f'{message.data[4]:02x}'
        elif column is TUI.COLUMN_BODY_BYTE_5:
             return f'{message.data[5]:02x}'
        elif column is TUI.COLUMN_BODY_BYTE_6:
             return f'{message.data[6]:02x}'
        elif column is TUI.COLUMN_BODY_BYTE_7:
            return f'{message.data[7]:02x}'
        elif column is TUI.COLUMN_COUNT:
            return str(self.counts[message.arbitration_id])
        elif column is TUI.COLUMN_CHANGES:
            return str(self.changes[message.arbitration_id])
 
    def getColumnIntForMessage(self, message, column):
        if column is TUI.COLUMN_TIMESTAMP:
            return message.timestamp
        elif column is TUI.COLUMN_MSGID:
            return message.arbitration_id
        elif column is TUI.COLUMN_BODY_BYTE_0:
            return message.data[0]
        elif column is TUI.COLUMN_BODY_BYTE_1:
            return message.data[1]
        elif column is TUI.COLUMN_BODY_BYTE_2:
            return message.data[2]
        elif column is TUI.COLUMN_BODY_BYTE_3:
            return message.data[3]
        elif column is TUI.COLUMN_BODY_BYTE_4:
             return message.data[4]
        elif column is TUI.COLUMN_BODY_BYTE_5:
             return message.data[5]
        elif column is TUI.COLUMN_BODY_BYTE_6:
             return message.data[6]
        elif column is TUI.COLUMN_BODY_BYTE_7:
            return message.data[7]
        elif column is TUI.COLUMN_COUNT:
            return self.counts[message.arbitration_id]
        elif column is TUI.COLUMN_CHANGES:
            return self.changes[message.arbitration_id]

    def addMessage(self, message):
        self.tui.lock.acquire()
        found = False
        i = 0
        for presentMsg in self.messages:
            if presentMsg.arbitration_id == message.arbitration_id:
                # compare messages and check if something has changed
                found = True
                changed = False
                self.hilights[presentMsg.arbitration_id].clear()
                for i in range(0, min(len(presentMsg.data), len(message.data))):
                    if str(presentMsg.data[i]) != str(message.data[i]):
                        self.hilights[presentMsg.arbitration_id].append(self.tui.COLUMN_BODY_BYTE_0 + i)
                        presentMsg.data[i] = message.data[i]
                        changed = True
                if changed:
                    self.changes[presentMsg.arbitration_id] += 1
                break

        if not found:
            self.messages.append(message)
            self.counts[message.arbitration_id] = 0
            self.changes[message.arbitration_id] = 1

            if self.sort is not None:
                self.messages.sort(key = lambda x: self.getColumnIntForMessage(x, self.sort), reverse=self.sortAscending)

            self.hilights[message.arbitration_id] = [self.tui.COLUMN_TIMESTAMP, self.tui.COLUMN_MSGID, self.tui.COLUMN_COUNT, self.tui.COLUMN_BODY_BYTE_0, self.tui.COLUMN_BODY_BYTE_1, self.tui.COLUMN_BODY_BYTE_2, self.tui.COLUMN_BODY_BYTE_3, self.tui.COLUMN_BODY_BYTE_4, self.tui.COLUMN_BODY_BYTE_5, self.tui.COLUMN_BODY_BYTE_6, self.tui.COLUMN_BODY_BYTE_7]

        self.counts[message.arbitration_id] += 1
        self.lastMessage = message
        self.redraw()
        self.tui.lock.release()

    def clear(self):
        self.tui.lock.acquire()
        self.messages = [ ]
        self.counts = { }
        self.changes = { }
        self.hilights = { }
        self.window.clear()
        self.redraw()
        self.tui.lock.release()

    def setSort(self, column, ascending):
        self.tui.lock.acquire()
        self.sort = column
        self.sortAscending = ascending
        self.messages.sort(key = lambda x: self.getColumnIntForMessage(x, self.sort), reverse=self.sortAscending)
        self.window.clear()
        self.redraw()
        self.tui.lock.release()



class TUI():
    COLOR_MENU_SHORTCUT = 1
    COLOR_MENU_DESC = 2
    COLOR_HEADER = 3
    COLOR_MSG = 4
    COLOR_MSG_HILIGHT = 5
    COLOR_MSG_HILIGHT_OLD = 6

    COLUMN_TIMESTAMP = 1
    COLUMN_MSGID = 2
    COLUMN_COUNT = 3
    COLUMN_BODY_BYTE_0 = 4
    COLUMN_BODY_BYTE_1 = 5
    COLUMN_BODY_BYTE_2 = 6
    COLUMN_BODY_BYTE_3 = 7  
    COLUMN_BODY_BYTE_4 = 8
    COLUMN_BODY_BYTE_5 = 9
    COLUMN_BODY_BYTE_6 = 10
    COLUMN_BODY_BYTE_7 = 11
    COLUMN_CHANGES = 12

    visibleColumns = [COLUMN_MSGID, COLUMN_BODY_BYTE_0, COLUMN_BODY_BYTE_1, COLUMN_BODY_BYTE_2, COLUMN_BODY_BYTE_3, COLUMN_BODY_BYTE_4, COLUMN_BODY_BYTE_5, COLUMN_BODY_BYTE_6, COLUMN_BODY_BYTE_7, COLUMN_COUNT, COLUMN_CHANGES]

    def getColumnWidth(self, column):
        if column is TUI.COLUMN_TIMESTAMP:
            return 6
        elif column is TUI.COLUMN_MSGID:
            return 3
        elif column >= TUI.COLUMN_BODY_BYTE_0 and column <= TUI.COLUMN_BODY_BYTE_7:
            return 2
        elif column is TUI.COLUMN_COUNT:
            return 6

    def getColumnOffset(self, column):
        totalOffset = 0
        for col in self.visibleColumns:
            if col is column:
                return totalOffset
            totalOffset += self.getColumnWidth(col) + 3
        return -1

    def getColumnDescription(self, column):
        if column is TUI.COLUMN_TIMESTAMP:
            return "Stamp"
        elif column is TUI.COLUMN_MSGID:
            return "ID"
        elif column is TUI.COLUMN_COUNT:
            return "COUNT"
        elif column is TUI.COLUMN_BODY_BYTE_0:
            return "B0"
        elif column is TUI.COLUMN_BODY_BYTE_1:
            return "B1"
        elif column is TUI.COLUMN_BODY_BYTE_2:
            return "B2"
        elif column is TUI.COLUMN_BODY_BYTE_3:
            return "B3"
        elif column is TUI.COLUMN_BODY_BYTE_4:
            return "B4"
        elif column is TUI.COLUMN_BODY_BYTE_5:
            return "B5"
        elif column is TUI.COLUMN_BODY_BYTE_6:
            return "B6"
        elif column is TUI.COLUMN_BODY_BYTE_7:
            return "B7"
        elif column is TUI.COLUMN_CHANGES:
            return "CHANGES"


    def __init__(self):
        self.maxMessages = 256
        self.lock = threading.RLock()
        self.lock.acquire()
        self.sortBy = None
        self.sortAscending = False

        self.bottomMenu = BottomMenu(curses.newwin(1, curses.COLS, curses.LINES - 2, 0), self)
        self.messagesPad = MessagesPad(curses.newpad(self.maxMessages, curses.COLS - 2), 1, 0, curses.LINES - 3, curses.COLS - 2, self)
        self.messagesHeader = MessagesHeader(curses.newwin(1, curses.COLS, 0, 0), self)
        curses.init_pair(self.COLOR_MENU_SHORTCUT, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(self.COLOR_MENU_DESC, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(self.COLOR_HEADER, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(self.COLOR_MSG, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(self.COLOR_MSG_HILIGHT_OLD, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(self.COLOR_MSG_HILIGHT, curses.COLOR_BLACK, curses.COLOR_RED)

        self.lock.release()


    def redraw(self):
        self.lock.acquire()
        self.bottomMenu.redraw()
        self.messagesHeader.redraw()
        self.messagesPad.redraw()
        self.lock.release()

    def addMessage(self, message):
        self.lock.acquire()
        self.messagesPad.addMessage(message)
        self.lock.release()

    def nextSort(self):
        if self.sortBy is None:
            self.sortBy = 0
        else:
            self.sortBy += 1

        if self.sortBy >= len(self.visibleColumns):
            self.sortAscending = not self.sortAscending
            self.sortBy = 0

        self.messagesPad.setSort(self.visibleColumns[self.sortBy], self.sortAscending)
        self.messagesHeader.setSort(self.visibleColumns[self.sortBy], self.sortAscending)


def canReaderThread(can_interface, tui):
    for message in can.interface.Bus(channel = can_interface, bustype = bustype):
        tui.addMessage(message)


def canReader(can_interface):
    for message in can.interface.Bus(channel = can_interface, bustype = bustype):
        print(message)




def main():
    if len(sys.argv) < 2 or sys.argv[1] is None:
        print("Usage: {} <caninterface>".format(sys.argv[0]))
        return
#    canReader(sys.argv[1])
    curses.wrapper(cursesMain)



def cursesMain(stdscr):
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.timeout(0)
    run = True

    tui = TUI()

    canThread = threading.Thread(target = canReaderThread, args=(sys.argv[1], tui, ))
    canThread.start()

    stdscr.refresh()
    tui.redraw()
    while run:
        tui.lock.acquire()
        k = stdscr.getch()
        tui.lock.release()

        if k == curses.KEY_F10:
            run = False
        elif k == curses.KEY_F5:
            tui.messagesPad.window.clear()
        elif k == curses.KEY_F6:
            tui.nextSort()
        elif k == curses.KEY_F8:
            tui.messagesPad.clear()
 
        elif k == curses.KEY_UP:
            if tui.messagesPad.yOffset >= 1:
                tui.messagesPad.yOffset -= 1
        if k == curses.KEY_DOWN:
            tui.messagesPad.yOffset += 1
        tui.redraw()
        time.sleep(0.01)

    canThread.join()



main()
