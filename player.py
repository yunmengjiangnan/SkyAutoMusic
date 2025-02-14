import time
import threading
from utils import press_key, release_all_keys, get_key_mapping
import keyboard
import random

def play_song(song_data, stop_event, speed_factor, log_window, initial_progress=0, 
              delay_enabled=False, delay_min=200, delay_max=500):
    # 预处理音符数据
    notes = song_data.get("songNotes", []) if isinstance(song_data, dict) else song_data
    if not notes:
        log_window.log("没有找到可播放的音符数据")
        return
        
    first_time = notes[0].get("time", 0) if isinstance(notes[0], dict) else notes[0][1]
    last_time = notes[-1].get("time", 0) if isinstance(notes[-1], dict) else notes[-1][1]
    total_duration = last_time - first_time
    
    key_map = {note.get("key") if isinstance(note, dict) else note[0]: get_key_mapping(note.get("key") if isinstance(note, dict) else note[0]) for note in notes}
    
    start_time = time.perf_counter() - (first_time / 1000 / speed_factor)
    pause_start_time = 0
    pause_total_time = 0
    
    start_position = getattr(log_window, 'seek_position', initial_progress)
    if start_position > 0:
        current_index = next(i for i, note in enumerate(notes) if (note.get("time", 0) if isinstance(note, dict) else note[1] - first_time) / total_duration * 100 >= start_position)
        notes = notes[current_index:]
        first_time = notes[0].get("time", 0) if isinstance(notes[0], dict) else notes[0][1]
        start_time = time.perf_counter() - (first_time / 1000 / speed_factor)
        if hasattr(log_window, 'update_play_progress'):
            log_window.update_play_progress(start_position)
    
    current_chord = []
    current_time = 0
    
    for i, note in enumerate(notes):
        if stop_event.is_set():
            release_all_keys()
            return
            
        while getattr(log_window, 'paused', False):
            if stop_event.is_set():
                release_all_keys()
                return
            if pause_start_time == 0:
                pause_start_time = time.perf_counter()
                release_all_keys()
            time.sleep(0.1)
            continue
            
        if pause_start_time > 0:
            pause_duration = time.perf_counter() - pause_start_time
            pause_total_time += pause_duration
            pause_start_time = 0
            start_time += pause_duration
        
        key = note.get("key") if isinstance(note, dict) else note[0]
        note_time = (note.get("time", 0) if isinstance(note, dict) else note[1]) / 1000 / speed_factor
        
        if i < len(notes) - 1:
            next_note = notes[i + 1]
            next_time = (next_note.get("time", 0) if isinstance(next_note, dict) else next_note[1]) / 1000 / speed_factor
            if abs(next_time - note_time) < 0.05:
                current_chord.append(key)
                current_time = note_time
                continue
        
        if current_chord:
            current_chord.append(key)
            play_chord(current_chord, current_time, start_time, key_map, log_window, delay_enabled, delay_min, delay_max, first_time, total_duration, note)
            current_chord = []
        else:
            play_single_key(key, note_time, start_time, key_map, log_window, delay_enabled, delay_min, delay_max, first_time, total_duration, note)
    
    release_all_keys()
    log_window.log("演奏结束")

def play_chord(chord, chord_time, start_time, key_map, log_window, delay_enabled, delay_min, delay_max, first_time, total_duration, note):
    sleep_time = chord_time - (time.perf_counter() - start_time)
    if sleep_time > 0:
        time.sleep(sleep_time)
    try:
        for chord_key in chord:
            keyboard.press(key_map[chord_key])
        if delay_enabled:
            time.sleep(random.randint(delay_min, delay_max) / 1000.0)
        else:
            time.sleep(0.1)
        for chord_key in chord:
            keyboard.release(key_map[chord_key])
        update_progress(log_window, first_time, total_duration, note)
    except Exception as e:
        log_window.log(f"按键错误: {str(e)}")
        release_all_keys()

def play_single_key(key, note_time, start_time, key_map, log_window, delay_enabled, delay_min, delay_max, first_time, total_duration, note):
    sleep_time = note_time - (time.perf_counter() - start_time)
    if sleep_time > 0:
        time.sleep(sleep_time)
    try:
        keyboard.press(key_map[key])
        if delay_enabled:
            time.sleep(random.randint(delay_min, delay_max) / 1000.0)
        else:
            time.sleep(0.1)
        keyboard.release(key_map[key])
        update_progress(log_window, first_time, total_duration, note)
    except Exception as e:
        log_window.log(f"按键错误 {key}: {str(e)}")
        release_all_keys()

def update_progress(log_window, first_time, total_duration, note):
    current_time = note.get("time", 0) if isinstance(note, dict) else note[1]
    progress = (current_time - first_time) / total_duration * 100
    if hasattr(log_window, 'update_play_progress'):
        log_window.update_play_progress(progress)