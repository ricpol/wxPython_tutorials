#!/usr/bin/env python
# -*- coding: cp1252 -*-
"""
Confronto colori. 
Una utility per scegliere e confrontare i colori in diversi modi. 
Questo modulo contiene le finestre secondarie dell'interfaccia.

Questa versione del programma e' puramente dimostrativa: questo modulo 
(e il suo compagno color_main.py) sono il codice allegato al tutorial 
"wxPython: tutorial su tecniche di programmazione OOP". 
Per questa ragione la documentazione interna e' lacunosa (e in italiano). 
Si rimanda al tutorial per maggiori chiarimenti.

(c) 2011 Riccardo Polignieri (ric.pol@libero.it)
licenza: GPL
"""

from collections import OrderedDict
import wx
from wx.lib.pubsub import Publisher

LAB_COL_1 = 'COLORE  1'
LAB_COL_2 = 'COLORE  2'

TOPIC_ROOT = 'color_change' # il topic piu' generale di cui abbiamo bisogno
TOPIC_COL1 = 'col1_changed' # il topic che segnala il cambiamento del colore 1
TOPIC_COL2 = 'col2_changed' # il topic che segnala il cambiamento del colore 2

# vedi AVAILABLE_AREAS in fondo al modulo 
# per la lista dei tipi di area di confronto disponibili

__all__ = ['getAvailableTables', 'ConfrontWindow']

# -----------------------------------------------------------------------------
# due funzioni di convenienza

def getAvailableTables():
    "Restituisce l'elenco delle tavole di confronto disponibili."
    return AVAILABLE_AREAS.keys()
    
def getConfrontArea(parent, area_type):
    "Restituisce l'istanza di un'area di confronto."
    area, kwargs = AVAILABLE_AREAS[area_type]
    return area(parent, **kwargs)

# -----------------------------------------------------------------------------
# ConfrontWindow (il MiniFrame che "contiene" le aree di confronto vere e propie)

class ConfrontWindow(wx.MiniFrame):
    def __init__(self, *args, **kwargs):
        kwargs['style'] = wx.CAPTION|wx.SYSTEM_MENU|wx.CLOSE_BOX|wx.RESIZE_BORDER
        area_type = kwargs.pop('area_type')
        wx.MiniFrame.__init__(self, *args, **kwargs)
        
        p = wx.Panel(self)
        self.area = getConfrontArea(p, area_type)
        self.connect_button = wx.ToggleButton(p, -1, 'connetti')
        
        self.connect_button.Bind(wx.EVT_TOGGLEBUTTON, self.on_connect)
        
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(self.area, 1, wx.EXPAND)
        s.Add(self.connect_button, 0, wx.EXPAND|wx.ALL, 5)
        p.SetSizer(s)
        self.SetSize((200, 200))
        
    def on_connect(self, evt):
        "Mette in ascolto l'area di confronto per eventuali cambi di colore."
        if self.connect_button.GetValue():
            self.connect_button.SetLabel('disconnetti')
            Publisher().subscribe(self.area._listener, TOPIC_ROOT)
        else:
            self.connect_button.SetLabel('connetti')
            Publisher().unsubscribe(self.area._listener)

# -----------------------------------------------------------------------------
# lo scheletro (una classe astratta) per le varie tavole di confronto

class BaseConfrontArea(wx.Panel):  
    def __init__(self, *args, **kwargs):
        "Costruisce la parte non-specifica dell'area di confronto."
        wx.Panel.__init__(self, *args, **kwargs)
        self.color_1 = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.color_2 = wx.TextCtrl(self, style=wx.TE_READONLY)
        
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(self.specific_layout(), 1, wx.EXPAND, 0)
        s1 = wx.GridSizer(2, 2, 2, 2)
        s1.Add(wx.StaticText(self, -1, LAB_COL_1), 0, wx.ALIGN_CENTER_HORIZONTAL)
        s1.Add(wx.StaticText(self, -1, LAB_COL_2), 0, wx.ALIGN_CENTER_HORIZONTAL)
        s1.Add(self.color_1, 1, wx.EXPAND)
        s1.Add(self.color_2, 1, wx.EXPAND)
        s.Add(s1, 0, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(s)
        self.Fit()

    def _listener(self, msg):
        'Ascolta e parsa i messaggi in arrivo, e agisce di conseguenza.'
        if msg.topic[-1] == TOPIC_COL1:
            self.color_1.SetValue(str(msg.data))
            self.change_color_1(msg.data)
        elif msg.topic[-1] == TOPIC_COL2:
            self.color_2.SetValue(str(msg.data))
            self.change_color_2(msg.data)
    
    def specific_layout(self):
        "Costruisce il resto dell'area di confronto: restituisce un sizer."
        raise NotImplementedError, 'da implementare nelle sotto-classi!'
    
    def change_color_1(self, col):
        'Cambia effettivamente il colore 1.'
        raise NotImplementedError, 'da implementare nelle sotto-classi!'
    
    def change_color_2(self, col):
        'Cambia effettivamente il colore 2.'
        raise NotImplementedError, 'da implementare nelle sotto-classi!'

# -----------------------------------------------------------------------------
# le varie tavole di confronto

class FieldsConfrontArea(BaseConfrontArea):
    "Una tavola di confronto fatta da due aree (verticali o orizzontali)."
    def __init__(self, *args, **kwargs):
        self.direction = kwargs.pop('direction')
        BaseConfrontArea.__init__(self, *args, **kwargs)
        
    def specific_layout(self):
        self.col1 = wx.Panel(self)
        self.col2 = wx.Panel(self)

        s = wx.BoxSizer(self.direction)
        s.Add(self.col1, 1, wx.EXPAND)
        s.Add(self.col2, 1, wx.EXPAND)
        return s
        
    def change_color_1(self, col):
        self.col1.SetBackgroundColour(wx.Colour(*col))
        self.Refresh()
        
    def change_color_2(self, col):
        self.col2.SetBackgroundColour(wx.Colour(*col))
        self.Refresh()


class TextOnBgConfrontArea(BaseConfrontArea):
    "Una tavola di confronto fatta da un testo su uno sfondo."
    def specific_layout(self):
        self.txt = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        font_chooser = wx.Button(self, -1, 'Font...')
        
        font_chooser.Bind(wx.EVT_BUTTON, self.on_font)
        
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(self.txt, 1, wx.EXPAND, 0)
        s.Add(font_chooser, 0, wx.EXPAND|wx.ALL, 5)
        return s
    
    def on_font(self, evt):
        data = wx.FontData()
        data.EnableEffects(False)
        data.SetInitialFont(self.txt.GetFont())

        dlg = wx.FontDialog(self, data)
        if dlg.ShowModal() == wx.ID_OK:
            font = dlg.GetFontData().GetChosenFont()
            self.txt.SetFont(font)
        dlg.Destroy()

    def change_color_1(self, col):
        self.txt.SetBackgroundColour(wx.Colour(*col))
        self.Refresh()
        
    def change_color_2(self, col):
        self.txt.SetForegroundColour(wx.Colour(*col))
        self.Refresh()

# -----------------------------------------------------------------------------
# lista delle tavole di confronto disponibili

AVAILABLE_AREAS = OrderedDict((
    ('Due aree (orizzontale)', (FieldsConfrontArea, {'direction':wx.VERTICAL})),
    ('Due aree (verticale)',   (FieldsConfrontArea, {'direction':wx.HORIZONTAL})),
    ('Testo su sfondo',        (TextOnBgConfrontArea, {})) ,
    ))


if __name__ == '__main__':
    print 'Questo modulo non deve essere eseguito. \n\n'
    print __doc__
    raw_input('\n\nenter per terminare')
