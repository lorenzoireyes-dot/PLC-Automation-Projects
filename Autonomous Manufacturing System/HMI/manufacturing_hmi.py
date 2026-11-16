"""Local OpenPLC manufacturing HMI. Requires pymodbus and customtkinter."""
import queue
import threading
import time
import tkinter as tk
import customtkinter as ctk
from pymodbus.client import ModbusTcpClient

HOST, PORT, UNIT = '127.0.0.1', 1502, 1
REG_NAMES = ('order', 'capacity', 'defect', 'accepted', 'rejected', 'total', 'remaining', 'batch', 'packages')
COIL_NAMES = {0:'start', 1:'stop', 2:'reset', 8:'running', 9:'warning', 10:'motor', 11:'processor', 12:'inspection', 13:'rejecting', 14:'packaging', 15:'complete', 16:'sensor', 17:'quality_fail'}
BG, PANEL, EDGE = '#101827', '#1a2638', '#34465d'
WHITE, MUTED, GREEN, RED, BLUE, AMBER = '#edf4ff', '#9bacc2', '#45d69b', '#ff737e', '#66b3ff', '#f5c66a'


def checked(response):
    if response.isError():
        raise RuntimeError(str(response))
    return response


def snapshot(client):
    r = checked(client.read_holding_registers(address=0, count=9, device_id=UNIT)).registers
    b = checked(client.read_coils(address=0, count=18, device_id=UNIT)).bits
    # IEC INT values are signed; Modbus registers are unsigned words.
    result = dict(zip(REG_NAMES, (v if v < 32768 else v - 65536 for v in r)))
    result.update({name: bool(b[i]) for i, name in COIL_NAMES.items()})
    return result


def worker(commands, events, closing):
    client = ModbusTcpClient(HOST, port=PORT, timeout=1, retries=0)
    connected = False
    pending_release = set()
    def write_coil(address, value):
        checked(client.write_coil(address=address, value=value, device_id=UNIT))
    def pulse(address):
        pending_release.add(address)
        try:
            write_coil(address, True)
            time.sleep(.25)
        finally:
            write_coil(address, False)
            pending_release.discard(address)
    def handle(action, payload):
        s = snapshot(client)
        if action == 'stop':
            pulse(1)
        elif action == 'reset':
            if s['running']:
                raise ValueError('Stop production before resetting counters.')
            pulse(2)
        elif action == 'apply':
            if s['running'] or s['total'] or s['batch'] or s['packages']:
                raise ValueError('Stop and reset counters before changing order settings.')
            checked(client.write_registers(address=0, values=list(payload), device_id=UNIT))
            time.sleep(.10)
            readback = snapshot(client)
            if tuple(readback[k] for k in ('order','capacity','defect')) != payload:
                raise ValueError('Settings did not persist in the PLC. Check variable mapping and forces.')
        elif action == 'start':
            if s['running']:
                raise ValueError('Production is already running.')
            if s['complete'] or s['accepted'] >= s['order']:
                raise ValueError('Reset counters before starting a completed order.')
            if not (1 <= s['order'] <= 1000 and 1 <= s['capacity'] <= 1000 and 0 <= s['defect'] <= 99):
                raise ValueError('Invalid settings. Apply a valid order, capacity and defect rate first.')
            if s['stop'] or s['reset']:
                raise ValueError('STOP or RESET is still active. Release it before starting.')
            pulse(0)
            time.sleep(.10)
            if not snapshot(client)['running']:
                raise ValueError('START was sent but SYSTEM_RUN did not activate. Check PLC forces and interlocks.')
    try:
        while not closing.is_set():
            try:
                action, payload = commands.get(timeout=.30)
            except queue.Empty:
                action, payload = 'poll', None
            try:
                if not connected:
                    if not client.connect():
                        raise ConnectionError('Runtime unavailable')
                    connected = True
                for address in tuple(pending_release):
                    write_coil(address, False)
                    pending_release.discard(address)
                if action != 'poll':
                    try:
                        handle(action, payload)
                    except ValueError as exc:
                        events.put(('message', str(exc)))
                    else:
                        events.put(('message', {'apply':'Settings applied and verified.', 'start':'START acknowledged.', 'stop':'STOP pulse sent.', 'reset':'RESET pulse sent.'}[action]))
                events.put(('snapshot', snapshot(client)))
            except Exception as exc:
                connected = False
                client.close()
                events.put(('offline', str(exc)))
            finally:
                if action != 'poll':
                    events.put(('done', None))
    finally:
        if connected:
            for address in tuple(pending_release):
                try:
                    write_coil(address, False)
                except Exception:
                    pass
        client.close()


class HMI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Manufacturing Control | OpenPLC HMI')
        self.geometry('1120x790')
        self.minsize(930, 740)
        self.configure(fg_color=BG)
        self.commands, self.events = queue.Queue(), queue.Queue()
        self.closing = threading.Event()
        self.data = None
        self.busy = False
        self.loaded = False
        self.phase = 0
        self.build()
        self.thread = threading.Thread(target=worker, args=(self.commands,self.events,self.closing), daemon=True)
        self.thread.start()
        self.protocol('WM_DELETE_WINDOW', self.close)
        self.after(80, self.tick)

    def label(self, parent, text, size=14, color=WHITE, bold=False, **kw):
        return ctk.CTkLabel(parent, text=text, text_color=color, font=ctk.CTkFont(size=size, weight='bold' if bold else 'normal'), **kw)

    def panel(self, parent):
        return ctk.CTkFrame(parent, fg_color=PANEL, corner_radius=12, border_width=1, border_color=EDGE)

    def build(self):
        header = ctk.CTkFrame(self, fg_color='transparent')
        header.pack(fill='x', padx=24, pady=(18,12))
        self.label(header,'MANUFACTURING CONTROL',26,bold=True).pack(side='left')
        self.connection = self.label(header,'CONNECTING',14,AMBER,bold=True)
        self.connection.pack(side='right')
        self.label(self,'AUTONOMOUS CUSTOMER ORDER FULFILLMENT  /  OPENPLC RUNTIME V4  /  MODBUS TCP',12,MUTED).pack(anchor='w',padx=24,pady=(0,12))
        config = self.panel(self)
        config.pack(fill='x',padx=24,pady=(0,12))
        self.entries = {}
        for i,(key,title) in enumerate((('order','Order quantity'),('capacity','Batch capacity'),('defect','Defect probability (%)'))):
            config.grid_columnconfigure(i,weight=1)
            self.label(config,title,13,MUTED).grid(row=0,column=i,sticky='w',padx=15,pady=(10,2))
            entry = ctk.CTkEntry(config, width=145, height=35, fg_color=BG, border_color=EDGE)
            entry.grid(row=1,column=i,sticky='ew',padx=15,pady=(0,12))
            self.entries[key]=entry
        self.apply = ctk.CTkButton(config,text='APPLY SETTINGS',height=35,fg_color='#2766a6',command=self.apply_settings)
        self.apply.grid(row=1,column=3,padx=15,pady=(0,12))
        self.visual = self.panel(self)
        self.visual.pack(fill='both',expand=True,padx=24,pady=(0,12))
        self.stage = self.label(self.visual,'AWAITING PLC CONNECTION',19,WHITE,True)
        self.stage.pack(pady=(12,0))
        self.canvas = tk.Canvas(self.visual,bg=PANEL,highlightthickness=0,height=190)
        self.canvas.pack(fill='both',expand=True,padx=12,pady=(0,8))
        stats = ctk.CTkFrame(self,fg_color='transparent')
        stats.pack(fill='x',padx=24,pady=(0,12))
        self.stats={}
        for i,(key,title,color) in enumerate((('accepted','ACCEPTED',GREEN),('rejected','REJECTED',RED),('total','PROCESSED',WHITE),('remaining','REMAINING',WHITE),('packages','PACKAGES',BLUE),('yield','QUALITY YIELD',AMBER))):
            stats.grid_columnconfigure(i,weight=1,uniform='stat')
            card=self.panel(stats); card.grid(row=0,column=i,sticky='nsew',padx=(0 if i==0 else 4,0 if i==5 else 4))
            self.label(card,title,11,MUTED,True).pack(pady=(10,0))
            value=self.label(card,'—',29,color,True); value.pack(pady=(0,8)); self.stats[key]=value
        progress=self.panel(self); progress.pack(fill='x',padx=24,pady=(0,12))
        self.progress_text=self.label(progress,'Order progress: —',14,WHITE,True); self.progress_text.pack(anchor='w',padx=15,pady=(8,4))
        self.progress=ctk.CTkProgressBar(progress,progress_color=GREEN,fg_color=EDGE,height=12); self.progress.pack(fill='x',padx=15,pady=(0,6)); self.progress.set(0)
        self.batch_text=self.label(progress,'Batch: —',12,MUTED); self.batch_text.pack(anchor='w',padx=15,pady=(0,8))
        controls=ctk.CTkFrame(self,fg_color='transparent'); controls.pack(fill='x',padx=24)
        self.buttons={}
        for i,(action,label,color) in enumerate((('start','START PRODUCTION','#16724e'),('stop','STOP','#a33446'),('reset','RESET COUNTERS','#34465d'))):
            controls.grid_columnconfigure(i,weight=1)
            btn=ctk.CTkButton(controls,text=label,height=40,fg_color=color,command=lambda a=action:self.send(a)); btn.grid(row=0,column=i,sticky='ew',padx=4); self.buttons[action]=btn
        self.message=self.label(self,'Waiting for live PLC data.',12,MUTED,wraplength=950); self.message.pack(fill='x',padx=24,pady=(5,8))
        self.refresh_controls()

    def send(self, action, payload=None):
        if self.busy or self.data is None: return
        self.busy=True; self.refresh_controls(); self.commands.put((action,payload))

    def apply_settings(self):
        try:
            values=tuple(int(self.entries[k].get()) for k in ('order','capacity','defect'))
            if not (1<=values[0]<=1000 and 1<=values[1]<=1000 and 0<=values[2]<=99):
                raise ValueError
        except ValueError:
            self.message.configure(text='Enter order and capacity from 1 to 1000, defect probability from 0 to 99.',text_color=AMBER); return
        self.send('apply',values)

    def refresh_controls(self):
        s=self.data
        enabled=s is not None and not self.busy
        idle=enabled and not s['running']
        editable=idle and not (s['total'] or s['batch'] or s['packages'])
        for entry in self.entries.values(): entry.configure(state='normal' if editable else 'disabled')
        self.apply.configure(state='normal' if editable else 'disabled')
        self.buttons['start'].configure(state='normal' if idle and not s['complete'] and s['accepted']<s['order'] else 'disabled')
        self.buttons['stop'].configure(state='normal' if enabled and s['running'] else 'disabled')
        self.buttons['reset'].configure(state='normal' if idle else 'disabled')

    def update_data(self,s):
        self.data=s
        self.connection.configure(text='●  PLC CONNECTED',text_color=GREEN)
        if not self.loaded:
            for k,entry in self.entries.items():
                entry.configure(state='normal'); entry.delete(0,'end'); entry.insert(0,str(s[k]))
            self.loaded=True
        for k,label in self.stats.items():
            label.configure(text=(f"{100*s['accepted']/s['total']:.1f}%" if s['total']>0 else '—') if k=='yield' else str(s[k]))
        self.progress_text.configure(text=f"Order progress: {s['accepted']} / {s['order']} accepted")
        self.progress.set(max(0,min(1,s['accepted']/s['order'])) if s['order']>0 else 0)
        self.batch_text.configure(text=f"Current batch: {s['batch']} / {s['capacity']}  |  Live settings: order {s['order']} • defect rate {s['defect']}%")
        self.refresh_controls()

    def draw(self):
        c=self.canvas; c.delete('all'); w=max(c.winfo_width(),700); h=max(c.winfo_height(),155)
        s=self.data
        if not s: text='PLC OFFLINE / CONNECTING'; active=-1
        elif s['complete']: text='ORDER FULFILLED'; active=-1
        elif not s['running']: text='READY FOR CUSTOMER ORDER'; active=-1
        elif s['warning']: text='STARTUP WARNING'; active=-1
        elif s['packaging']: text='PACKAGING ACCEPTED PRODUCTS'; active=4
        elif s['rejecting']: text='REJECTING DEFECTIVE PRODUCT'; active=3
        elif s['inspection']: text='QUALITY INSPECTION'; active=2
        elif s['processor']: text='MANUFACTURING IN PROGRESS'; active=1
        elif s['motor']: text='FEEDING NEXT PRODUCT'; active=0
        else: text='PRODUCT CLEARANCE'; active=-1
        self.stage.configure(text=text,text_color=RED if active==3 else AMBER if s and s['warning'] else GREEN if s and s['complete'] else WHITE)
        xs=[w*(i+.5)/5 for i in range(5)]; bw=min(142,w/5-15); belt=h-48
        for i,(x,name) in enumerate(zip(xs,('FEED','PROCESS','INSPECT','REJECT','PACKAGE'))):
            col=(RED if i==3 else GREEN) if i==active else EDGE
            c.create_rectangle(x-bw/2,12,x+bw/2,70,fill='#243d36' if i==active and i!=3 else '#432b38' if i==active else BG,outline=col,width=2)
            c.create_oval(x-5,21,x+5,31,fill=col,outline='')
            c.create_text(x,51,text=name,fill=WHITE,font=('Segoe UI',11,'bold'))
            c.create_line(x,70,x,belt,fill=EDGE,dash=(3,4))
        c.create_rectangle(15,belt,w-15,belt+27,fill=BG,outline=EDGE,width=2)
        for x in range(29,int(w)-16,27):
            c.create_oval(x-9,belt+4,x+9,belt+22,outline=BLUE if s and s['motor'] else EDGE,width=1)
        if s and (s['sensor'] or active in (0,4)):
            x=xs[active] if active>=0 else xs[1]
            if active==0: x=25+(xs[1]-25)*(self.phase%24)/24
            color=RED if active==3 else BLUE
            c.create_rectangle(x-18,belt-19,x+18,belt,fill=color,outline='')
        c.create_text(w/2,h-8,text='Station activity from PLC coils  •  Product position is schematic',fill=MUTED,font=('Segoe UI',10))

    def tick(self):
        while True:
            try: kind,value=self.events.get_nowait()
            except queue.Empty: break
            if kind=='snapshot': self.update_data(value)
            elif kind=='offline':
                self.data=None; self.loaded=False; self.connection.configure(text='●  PLC OFFLINE',text_color=RED)
                for label in self.stats.values(): label.configure(text='—')
                self.progress.set(0); self.progress_text.configure(text='Order progress: unavailable'); self.batch_text.configure(text='Batch: unavailable')
                self.message.configure(text=f'Communication error: {value}',text_color=RED); self.refresh_controls()
            elif kind=='message': self.message.configure(text=value,text_color=MUTED)
            elif kind=='done': self.busy=False; self.refresh_controls()
        self.phase+=1; self.draw(); self.after(100,self.tick)

    def close(self):
        # Closing an HMI does not stop the independent PLC controller.
        self.closing.set(); self.destroy()

if __name__=='__main__':
    ctk.set_appearance_mode('dark')
    HMI().mainloop()
