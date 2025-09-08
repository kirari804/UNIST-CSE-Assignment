#include <SDL2/SDL.h>
#include <cmath>
#include <iostream>
#include <string>
#include <climits>
using namespace std;


struct voice {
    double freq = 0.0;
    double ampl = 0.0;
    double lowpass = 0.0;  //smoothing factor in lowpass filtering
    // double phase = 0.0;
    double last_sampl = 0.0;  //output after lowpass filtering
};

struct playback_data {
    voice voices[4];
    unsigned long long position = 0;
};



static void play_audio (void* u, unsigned char* stream, int len) {

    short* buffer = (short*)stream;
    size_t num_samples = len / sizeof(short);
    playback_data* data = (playback_data*) u;
    for (size_t i = 0; i<num_samples; i++, data->position++) {
        double mix_sample = 0.0;

        for (int j = 0;  j<4; j++){
            voice& voice = data->voices[j];
            if (voice.ampl==0 || voice.freq==0)
                continue;
            double cycle_length = 44100/voice.freq;

            double cycle_count;
            double phase = modf(data->position/cycle_length, &cycle_count);
            
            double origin_sampl;
            if (phase < 0.5) //square wave
                origin_sampl = 1.0;
            else    
                origin_sampl = -1.0;

            voice.last_sampl = (1-voice.lowpass)*origin_sampl + voice.lowpass*voice.last_sampl; //lowpass filter formula
            mix_sample += voice.last_sampl*voice.ampl; //add up values
            } 
        //     voice.phase += voice.freq / 44100.0;
        //     if (voice.phase >= 1.0) 
        //         voice.phase -= 1.0;

        // }
        if (mix_sample > 1.0) 
            mix_sample = 1.0;
        if (mix_sample < -1.0)
            mix_sample = -1.0;
        buffer[i] = (short)(mix_sample * SHRT_MAX); //convert final value into 16-bit int


    }

}


int main() {
    if (SDL_Init(SDL_INIT_AUDIO) < 0 ) {
        cerr << "SDL could not initialize! SDL_Error: " << SDL_GetError() << endl;
        return 1;
    }
    playback_data data;


    SDL_AudioSpec audio_spec = { .freq =  44100, .format = AUDIO_S16SYS, .channels = 1,
                                .samples = 2048, .callback = play_audio, .userdata = &data};

    if (SDL_OpenAudio(&audio_spec, nullptr)<0) {
        cerr << "SDL_OpenAudio failed: " << SDL_GetError();
        SDL_Quit();
        return 1;
    } 

    SDL_PauseAudio(false);

    string cmd;
    
    while (cin>>cmd) {
        if (cmd == "freq") {
            int voice;
            double f;
            cin >> voice >> f;
            if (voice >= 0 && voice < 4)
                data.voices[voice].freq = f;
        }
        else if (cmd == "ampl") {
            int voice;
            double a;
            cin >> voice >> a;
            if (voice >= 0 && voice < 4)
                data.voices[voice].ampl = a;
        }
        else if (cmd == "lowpass") {
            int voice;
            double amt;
            cin >> voice >> amt;
            if (voice >= 0 && voice < 4)
                data.voices[voice].lowpass = amt;
        }
        else if (cmd == "delay") {
            long millis;
            cin >> millis;
            SDL_Delay(millis);
        }
        else if (cmd == "quit")
            break;
    }

    SDL_CloseAudio();
    SDL_Quit();
    return 0;
}