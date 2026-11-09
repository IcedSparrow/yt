from faster_whisper import WhisperModel
import json,sys
m=WhisperModel("../npmmodel/m", device="cpu", compute_type="int8")
import numpy as np,wave
w=wave.open("audio16.wav");a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
segs,info=m.transcribe(a, language="pl", word_timestamps=True, vad_filter=False, beam_size=5,
  initial_prompt="Rolex Deepsea Challenge. Rów Mariański. James Cameron. tytan RLX. Zegarkidawida.")
out=[]
for s in segs:
  for w in s.words: out.append([round(w.start,3),round(w.end,3),w.word])
  print(f"{s.start:.2f}-{s.end:.2f} {s.text}",flush=True)
json.dump(out,open(f"words_{sys.argv[1]}.json","w"),ensure_ascii=False)
