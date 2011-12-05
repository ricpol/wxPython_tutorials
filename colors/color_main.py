#!/usr/bin/env python
# -*- coding: cp1252 -*-
"""
Confronto colori. 
Una utility per scegliere e confrontare i colori in diversi modi. 
Questo modulo contiene gli elementi della finestra principale dell'interfaccia.

Questa versione del programma e' puramente dimostrativa: questo modulo 
(e il suo compagno confront_area.py) sono il codice allegato al tutorial 
"wxPython: tutorial su tecniche di programmazione OOP". 
Per questa ragione la documentazione interna e' lacunosa (e in italiano). 
Si rimanda al tutorial per maggiori chiarimenti.

(c) 2011 Riccardo Polignieri (ric.pol@libero.it)
licenza: GPL
"""

import wx
from wx.lib.pubsub import Publisher
from confront_area import *

LAB_COL_1 = 'COLORE  1'
LAB_COL_2 = 'COLORE  2'

TOPIC_ROOT = 'color_change' # il topic piu' generale di cui abbiamo bisogno
TOPIC_COL1 = 'col1_changed' # il topic che segnala il cambiamento del colore 1
TOPIC_COL2 = 'col2_changed' # il topic che segnala il cambiamento del colore 2


# -----------------------------------------------------------------------------
# il componente-base: SpinSlider

class SpinSliderEvent(wx.PyCommandEvent):
    "L'evento che lo SpinSlider emette quando ne viene modificato il valore."
    def __init__(self, evtType, id):
        wx.PyCommandEvent.__init__(self, evtType, id)
        
myEVT_SPINSLIDER = wx.NewEventType()
EVT_SPINSLIDER = wx.PyEventBinder(myEVT_SPINSLIDER, 1)

class SpinSlider(wx.Panel):
    'Un componente formato da uno slider e uno spin collegati tra loro.'
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        
        self.spin = wx.SpinCtrl(self)
        self.slider = wx.Slider(self, style=wx.SL_VERTICAL|wx.SL_INVERSE)
        self.label = wx.StaticText(self)
        
        self.spin.Bind(wx.EVT_SPINCTRL, self._on_spin)
        self.slider.Bind(wx.EVT_SLIDER, self._on_slider)
        
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(self.label, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        s.Add(self.spin, 0, wx.EXPAND|wx.ALL, 5)
        s.Add(self.slider, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        self.SetSizer(s)
        self.Fit()
    
    def _on_spin(self, evt):
        self.slider.SetValue(self.spin.GetValue())
        self._post_custom_event()
    
    def _on_slider(self, evt):
        self.spin.SetValue(self.slider.GetValue())
        self._post_custom_event()
        
    def _post_custom_event(self):
        "Crea ed emette l'evento personalizzato EVT_SPINSLIDER." 
        evt = SpinSliderEvent(myEVT_SPINSLIDER, self.GetId())
        self.GetEventHandler().ProcessEvent(evt)
    
    def SetValue(self, value):
        self.spin.SetValue(value)
        self.slider.SetValue(value)
        
    def GetValue(self):
        return self.spin.GetValue()
        
    def SetLabel(self, label):
        self.label.SetLabel(label)
        self.Refresh()
    
    def SetMin(self, min_):
        self.spin.SetRange(min_, self.spin.GetMax())
        self.slider.SetMin(min_)
            
    def SetMax(self, max_):
        self.spin.SetRange(self.spin.GetMin(), max_)
        self.slider.SetMax(max_)
    
    def GetMin(self):
        return self.spin.GetMin()
    
    def GetMax(self):
        return self.spin.GetMax()
        
# -----------------------------------------------------------------------------
# SliderPanel (componente formato da tre SpinSlider messi insieme)

class SliderPanel(wx.Panel):
    'Un componente formato da tre SpinSlider, per mappare un colore RGB.'
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        
        self.title = wx.StaticText(self)
        self.color_area = wx.Panel(self, size=(-1, 40))
        comp_1 = SpinSlider(self)
        comp_2 = SpinSlider(self)
        comp_3 = SpinSlider(self)
        self.components = (comp_1, comp_2, comp_3)
    
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(self.title, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        s.Add(self.color_area, 0, wx.FIXED_MINSIZE|wx.EXPAND, 0)
        s1 = wx.BoxSizer()
        for ctl in self.components:
            s1.Add(ctl, 1, wx.EXPAND, 0)
        s.Add(s1, 1, wx.EXPAND, 0)
        self.SetSizer(s)
        self.Fit()
        
        self.Bind(EVT_SPINSLIDER, self._on_spinslider)
        
    def _on_spinslider(self, evt):
        "Intercetta l'EVT_SPINSLIDER, lasciando poi che si propaghi."
        self.color_area.SetBackgroundColour(wx.Colour(*self.GetValue()))
        self.color_area.Refresh()
        # evt.Skip() # vedi tutorial per chiarimenti...

    def SetValue(self, value):
        for i, ctl in enumerate(self.components):
            ctl.SetValue(value[i])
        self.color_area.SetBackgroundColour(value)
        self.color_area.Refresh()
            
    def GetValue(self):
        return [i.GetValue() for i in self.components]
    
    def SetLabel(self, label):
        for i, ctl in enumerate(self.components):
            ctl.SetLabel(label[i])
        
    def SetTitleLabel(self, label):
        self.title.SetLabel(label)
        self.Refresh()
    
    def SetMax(self, max_):
        for ctl, value in zip(self.components, max_):
            ctl.SetMax(value)
    
    def SetMin(self, min_):
        for ctl, value in zip(self.components, min_):
            ctl.SetMin(value)
            
    def GetMax(self):
        return [i.GetMax() for i in self.components]
        
    def GetMin(self):
        return [i.GetMin() for i in self.components]
        
# -----------------------------------------------------------------------------
# MainColorConfront (la finestra principale!)

class MainColorConfront(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        p = wx.Panel(self)
        p.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
        
        self.color_1 = SliderPanel(p)
        self.color_2 = SliderPanel(p)
        self.color_1.SetTitleLabel(LAB_COL_1)
        self.color_2.SetTitleLabel(LAB_COL_2)
        for ctl in (self.color_1, self.color_2):
            ctl.SetMin((0, 0, 0))
            ctl.SetMax((255, 255, 255))
            ctl.SetValue((0, 0, 0))
            ctl.SetLabel('RGB')
        
        self.table_chooser = wx.ComboBox(p, choices=getAvailableTables(), 
                                         style=wx.CB_DROPDOWN|wx.CB_READONLY)
        open_table = wx.Button(p, -1, 'Apri tavola')
        
        open_table.Bind(wx.EVT_BUTTON, self.on_open_table)
        self.color_1.Bind(EVT_SPINSLIDER, self.on_color_1_changed)
        self.color_2.Bind(EVT_SPINSLIDER, self.on_color_2_changed)

        s = wx.BoxSizer(wx.VERTICAL)
        s1 = wx.BoxSizer()
        s1.Add(self.color_1, 1, wx.EXPAND|wx.ALL, 5)
        s1.Add((20, 20))
        s1.Add(self.color_2, 1, wx.EXPAND|wx.ALL, 5)
        s.Add(s1, 1, wx.EXPAND, 0)
        s1 = wx.BoxSizer()
        s1.Add(self.table_chooser, 1, wx.EXPAND|wx.ALL, 5)
        s1.Add(open_table, 0, wx.ALL, 5)
        s.Add(s1, 0, wx.EXPAND, 0)
        p.SetSizer(s)
    
    def on_color_1_changed(self, evt):
        "Pubblica un messaggio per segnalare che il colore 1 e' cambiato."
        Publisher().sendMessage((TOPIC_ROOT, TOPIC_COL1), self.color_1.GetValue())
        evt.Skip()
    
    def on_color_2_changed(self, evt):
        "Pubblica un messaggio per segnalare che il colore 2 e' cambiato."
        Publisher().sendMessage((TOPIC_ROOT, TOPIC_COL2), self.color_2.GetValue())
        evt.Skip()
        
    def on_open_table(self, evt):
        'Apre una tavola di confronto, tra quelle disponibili.'
        fr = ConfrontWindow(self, area_type=self.table_chooser.GetValue())
        fr.Show()


app = wx.App(False)  
MainColorConfront(None, -1, 'Confronto colori').Show()
app.MainLoop() 

