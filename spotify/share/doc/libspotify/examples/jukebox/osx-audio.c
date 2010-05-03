/*
 * Copyright (c) 2010 Spotify Ltd
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 *
 *
 * OSX AudioQueue output driver.
 *
 * This file is part of the libspotify examples suite.
 */

#include <AudioToolbox/AudioQueue.h>
#include "audio.h"

#define BUFFER_COUNT 3
static struct AQPlayerState {
    AudioStreamBasicDescription   desc;
    AudioQueueRef                 queue;
    AudioQueueBufferRef           buffers[BUFFER_COUNT];
    unsigned buffer_size;
} state;

static void audio_callback (void *aux, AudioQueueRef aq, AudioQueueBufferRef bufout)
{
    audio_fifo_t *af = aux;
    audio_fifo_data_t *afd = audio_get(af);

    bufout->mAudioDataByteSize = afd->nsamples * sizeof(short) * afd->channels;

    assert(bufout->mAudioDataByteSize <= state.buffer_size);
    memcpy(bufout->mAudioData, afd->samples, bufout->mAudioDataByteSize);

    AudioQueueEnqueueBuffer(state.queue, bufout, 0, NULL);
    free(afd);
}

void audio_init(audio_fifo_t *af)
{
    int i;
    TAILQ_INIT(&af->q);
    af->qlen = 0;

    pthread_mutex_init(&af->mutex, NULL);
    pthread_cond_init(&af->cond, NULL);

    bzero(&state, sizeof(state));

    state.desc.mFormatID = kAudioFormatLinearPCM;
    state.desc.mFormatFlags = kAudioFormatFlagIsSignedInteger	| kAudioFormatFlagIsPacked;
    state.desc.mSampleRate = 44100;
    state.desc.mChannelsPerFrame = 2;
    state.desc.mFramesPerPacket = 1;
    state.desc.mBytesPerFrame = sizeof (short) * state.desc.mChannelsPerFrame;
    state.desc.mBytesPerPacket = state.desc.mBytesPerFrame;
    state.desc.mBitsPerChannel = (state.desc.mBytesPerFrame*8)/state.desc.mChannelsPerFrame;
    state.desc.mReserved = 0;

    state.buffer_size = state.desc.mBytesPerFrame * state.desc.mSampleRate;

    if (noErr != AudioQueueNewOutput(&state.desc, audio_callback, af, NULL, NULL, 0, &state.queue)) {
	printf("audioqueue error\n");
	return;
    }

    // Start some empty playback so we'll get the callbacks that fill in the actual audio.
    for (i = 0; i < BUFFER_COUNT; ++i) {
	AudioQueueAllocateBuffer(state.queue, state.buffer_size, &state.buffers[i]);
	state.buffers[i]->mAudioDataByteSize = state.buffer_size;
	AudioQueueEnqueueBuffer(state.queue, state.buffers[i], 0, NULL);
    }
    if (noErr != AudioQueueStart(state.queue, NULL)) puts("AudioQueueStart failed");
}

void audio_fifo_flush(audio_fifo_t *af)
{
    audio_fifo_data_t *afd;

    pthread_mutex_lock(&af->mutex);

    while((afd = TAILQ_FIRST(&af->q))) {
	TAILQ_REMOVE(&af->q, afd, link);
	free(afd);
    }

    af->qlen = 0;
    pthread_mutex_unlock(&af->mutex);
}
