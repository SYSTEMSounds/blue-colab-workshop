import numpy as np
from audiolazy import midi2str,str2midi
from midiutil import MIDIFile #import library to make midi file, https://midiutil.readthedocs.io/en/1.2.1/


def map_value(value, min_value, max_value, min_result, max_result, power=1):
    '''maps value(s) from one range to another

    value: input value (int, float, list, or array)
    min_value,max_value: input value range
    min_result,max_result: output value range
    power: scaling parameter, linear mapping if set to 1
    
    Returns:
        int if both min_result and max_result are int, otherwise float
        list of int or float if value is a list
        array of int or float if value is an array'''
    
    value_input = value 
    
    #if list, convert to array
    if isinstance(value_input, list): value = np.array(value_input) 
        
    #validation
    if np.any(value < min_value) or np.any(value > max_value):
        raise ValueError(f'one or more values is outside of range [{min_value},{max_value}]!')
            
    #mapping
    result = min_result + ((value - min_value)/(max_value - min_value))**power*(max_result - min_result)
    
    #rounding
    if isinstance(min_result*max_result, int):
        if isinstance(value_input, int) or isinstance(value_input, float):
            result = round(result)
        if isinstance(value_input, list) or isinstance(value_input, np.ndarray):
            result = np.round(result).astype(int)
    
    # value_input was list, convert result into list
    if isinstance(value_input, list): result = result.tolist() 
        
    return result



def get_scale_notes(start_note, octaves, scale):
    '''gets scale note names
    
    start_note: string , ex. 'C2'
    octaves: int, number of octaves
    scale: string (from available) or custom list of scale steps (ex. [2,2,1,2,2,2,1])
    
    returns: list of note names (including root as highest note)
    '''
    
    scales = {
    'chromatic':[1,1,1,1,1,1,1,1,1,1,1,1],
        
    'major':[2,2,1,2,2,2,1],
    'minor':[2,1,2,2,1,2,2],
    'harmonicMinor':[2,1,2,2,1,3,1],
    'melodicMinor':[2,1,2,2,2,2,1],
        
    'ionian':[2,2,1,2,2,2,1],
    'dorian':[2,1,2,2,2,1,2],
    'phrygian':[1,2,2,2,1,2,2],
    'lydian':[2,2,2,1,2,2,1],
    'mixolydian':[2,2,1,2,2,1,2],
    'aeolian':[2,1,2,2,1,2,2],
    'lochrian':[1,2,2,1,2,2,2],
        
    'majorPent':[2,2,3,2,3],
    'minorPent':[3,2,2,3,2],

    'wholetone':[2,2,2,2,2,2],
    'diminished':[2,1,2,1,2,1,2,1],
        
    #add more here!
    }
    
    #get scale steps 
    if type(scale) is str:
        if scale not in scales.keys():
            raise ValueError(f'Scale name not recognized!')
        else:
            scale_steps = scales[scale]
    if type(scale) is list:
        scale_steps = scale
        
    #get note names for each scale step, in each octave
    note_names = []
    for octave in range(octaves):
        note_number = str2midi(start_note) + (12*octave) 
        
        for step in scale_steps:
            note_names.append(midi2str(note_number))
            note_number = note_number + step
            
    #add root as last note
    last_midi_note = str2midi(start_note) + (octaves*12) 
    note_names.append(midi2str(last_midi_note))
    
    #could alter function to return midi note numbers instead
    #note_numbers = [str2midi(n) for n in note_names]
            
    return note_names



def save_midi(events, out_filename, bpm=60):
    '''saves one track midi file with note events'''
    
    my_midi_file = MIDIFile(1) #one track 
    my_midi_file.addTempo(track=0, time=0, tempo=bpm) 

    for event in events:
        my_midi_file.addNote(track=0, channel=0, pitch=event['midi'], time=event['t'] , duration=event['dur'], volume=event['vel'])

    with open(out_filename + '.mid', "wb") as f:
        my_midi_file.writeFile(f) 
    print('saved ' + out_filename + '.mid')
    
    
def save_midi_cc(events, events_cc, out_filename, bpm=60):
    '''saves one track midi file with note events and control change events
    
    events: list of event dictionaries
    events_cc: list of control change event dictionaries
    out_filename: string, desired filename for mid file (_cc is appended)
    bpm: int or float, tempo in beats per minute'''
    
    my_midi_file = MIDIFile(1) #one track 
    my_midi_file.addTempo(track=0, time=0, tempo=bpm) 

    for event in events:
        my_midi_file.addNote(track=0, channel=0, pitch=event['midi'], time=event['t'] , duration=event['dur'], volume=event['vel'])

    for event_cc in events_cc:
        my_midi_file.addControllerEvent(track=0, channel=0, time=event_cc['t'], controller_number=event_cc['controller_number'], parameter=event_cc['parameter'])

    with open(out_filename + '_cc.mid', "wb") as f:
        my_midi_file.writeFile(f) 
    print('saved ' + out_filename + '_cc.mid')