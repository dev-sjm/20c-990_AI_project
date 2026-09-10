"""Focused checks for the public notebook format and musical transformations.

Run from the repository root: python -m unittest discover -s tests -v
No historical training data or model weights are needed.
"""
import ast
import json
from pathlib import Path
import tempfile
import unittest

import mido
import midiutil
import nbformat
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def cells(name):
    return json.loads((ROOT / 'notebooks' / name).read_text(encoding='utf-8'))['cells']


def code(name, index):
    return ''.join(cells(name)[index]['source'])


class NotebookChecks(unittest.TestCase):
    def test_notebook_format_and_clean_outputs(self):
        for path in (ROOT / 'notebooks').rglob('*.ipynb'):
            nb = nbformat.read(path, as_version=4)
            nbformat.validate(nb)
            for c in nb.cells:
                if c.cell_type == 'code':
                    self.assertEqual(c.outputs, [], str(path))
                    self.assertIsNone(c.execution_count)
        # Historical archives intentionally retain exploratory cell order/magics.
        for path in (ROOT / 'notebooks').glob('*.ipynb'):
            for c in nbformat.read(path, as_version=4).cells:
                if c.cell_type == 'code':
                    python = '\n'.join(line for line in c.source.splitlines()
                                       if not line.lstrip().startswith(('!', '%')))
                    ast.parse(python, filename=str(path))

    def test_chart_assignment(self):
        frame = pd.DataFrame({
            'rank': [1] * 320, 'date': ['1995-01-01'] * 320,
            'song': [f'Original fixture {i}' for i in range(320)],
            'artist': ['Synthetic'] * 320, 'last_week': [1] * 320,
            'weeks_on_chart': list(range(320, 0, -1))})
        env = {'BB': frame, 'pd': pd, 'Path': Path}
        exec(code('01_chart_selection.ipynb', 2), env)
        assignments = code('01_chart_selection.ipynb', 4).split('output_dir =')[0]
        exec(assignments, env)
        for name, start in [('Haewan',120), ('Boram',121), ('Dongjin',122)]:
            self.assertEqual(env[name]['song'].tolist(), frame.iloc[start:240:3]['song'].tolist())
        self.assertEqual(env['Jaemyung']['song'].tolist(), frame.iloc[240:300]['song'].tolist())

    def test_midi_to_two_four_bar_images(self):
        env = {'MidiFile': mido.MidiFile, 'np': np}
        for index in [4,5,6]:
            exec(code('03_prepare_dataset.ipynb', index), env)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'original_fixture.mid'
            mid = mido.MidiFile(ticks_per_beat=480)
            track = mido.MidiTrack()
            mid.tracks.append(track)
            # MIDI 48: first beat; MIDI 72: first beat of second four-bar half.
            track.extend([
                mido.Message('note_on', note=48, velocity=80, time=0),
                mido.Message('note_off', note=48, velocity=0, time=480),
                mido.Message('note_on', note=72, velocity=80, time=15*480),
                mido.Message('note_off', note=72, velocity=0, time=480)])
            mid.save(path)
            result = env['make_data_set_64']([str(path)])
            expected = np.zeros((2,64,64))
            expected[0,12,0:4] = 1  # MIDI 48 -> compressed row 12
            expected[1,24,0:4] = 1  # MIDI 72 -> compressed row 24
            np.testing.assert_array_equal(result, expected)

    def test_image_to_midi_pitch_duration_and_final_column(self):
        target = np.zeros((64,64))
        target[0,0:4] = 1       # MIDI 36, one beat
        target[24,60:64] = 1    # MIDI 72, sustained through last column
        target[63,63] = 1       # MIDI 111, only final sixteenth note
        with tempfile.TemporaryDirectory() as directory:
            env = {'np':np, 'midiutil':midiutil, 'target':target,
                   'OUTPUT_DIR':Path(directory), 'time':'fixture', 'ckpt':0,
                   'n':1, 'midi_bpm':100}
            exec(code('05_generate_midi.ipynb',7), env)
            self.assertEqual(env['sequence'], [
                {'pitch':36,'start_time':0.0,'length':1.0,'velocity':80},
                {'pitch':72,'start_time':15.0,'length':1.0,'velocity':80},
                {'pitch':111,'start_time':15.75,'length':0.25,'velocity':80}])
            mid = mido.MidiFile(Path(directory) / 'fixture_ckpt-0_1.mid')
            on = [m.note for t in mid.tracks for m in t if m.type=='note_on' and m.velocity]
            self.assertEqual(on, [36,72,111])

    def test_train_and_deploy_model_definitions_match(self):
        def definitions(name):
            found = {}
            for c in cells(name):
                if c['cell_type'] != 'code':
                    continue
                text = '\n'.join(line for line in ''.join(c['source']).splitlines()
                                 if not line.lstrip().startswith(('!', '%')))
                for node in ast.parse(text).body:
                    if isinstance(node, ast.FunctionDef) and node.name in {
                            'make_generator_model', 'make_discriminator_model'}:
                        found[node.name] = ast.dump(node, include_attributes=False)
            return found
        self.assertEqual(len(definitions('04_train_dcgan.ipynb')), 2)
        self.assertEqual(definitions('04_train_dcgan.ipynb'), definitions('05_generate_midi.ipynb'))


if __name__ == '__main__':
    unittest.main()
