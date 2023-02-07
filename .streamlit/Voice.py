# streamlit_audio_recorder by stefanrmmr (rs. analytics) - version April 2022

import os
import numpy as np
import streamlit as st
from io import BytesIO
import streamlit.components.v1 as components

def audiorec_demo_app(parent_dir, build_dir,st_audiorec):
    # STREAMLIT AUDIO RECORDER Instance
    val = st_audiorec()
    print(val)
    if isinstance(val, dict):  # retrieve audio data
        with st.spinner('retrieving audio-recording...'):
            ind, val = zip(*val['arr'].items())
            ind = np.array(ind, dtype=int)  # convert to np array
            val = np.array(val)             # convert to np array
            sorted_ints = val[ind]
            stream = BytesIO(b"".join([int(v).to_bytes(1, "big") for v in sorted_ints]))
            wav_bytes = stream.read()


        # wav_bytes contains audio data in format to be further processed
        # display audio data as received on the Python side
        #st.audio(wav_bytes, format='audio/wav')