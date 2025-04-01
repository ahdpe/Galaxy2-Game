import numpy as np
import wave
import random
import math

print("Создание placeholder WAV файлов...")

# Параметры звука
SAMPLE_RATE = 44100  # Частота дискретизации (Гц)
DURATION_SHORT = 0.15 # Длительность коротких звуков (секунды)
DURATION_MEDIUM = 0.3
AMPLITUDE = 32767 // 4 # Громкость (максимум для 16 бит = 32767), делаем тише

def generate_sine_wave(frequency, duration, sample_rate=SAMPLE_RATE, amplitude=AMPLITUDE):
    """Генерирует синусоиду."""
    t = np.linspace(0., duration, int(sample_rate * duration), endpoint=False)
    # Простая атака/затухание, чтобы не было щелчка
    attack_len = int(0.01 * sample_rate)
    decay_len = int(0.05 * sample_rate)
    envelope = np.ones_like(t)
    if len(t) > attack_len:
        envelope[:attack_len] = np.linspace(0, 1, attack_len)
    if len(t) > decay_len:
         envelope[-decay_len:] = np.linspace(1, 0, decay_len)

    wave_data = amplitude * np.sin(frequency * t * 2 * np.pi) * envelope
    return wave_data.astype(np.int16) # Преобразуем в 16-битный формат

def generate_noise(duration, sample_rate=SAMPLE_RATE, amplitude=AMPLITUDE):
    """Генерирует белый шум."""
    t = np.linspace(0., duration, int(sample_rate * duration), endpoint=False)
    # Затухание для шума
    decay_len = int(0.1 * sample_rate)
    envelope = np.ones_like(t)
    if len(t) > decay_len:
        envelope[-decay_len:] = np.linspace(1, 0, decay_len)

    noise_data = np.random.uniform(-amplitude, amplitude, int(sample_rate * duration)) * envelope
    return noise_data.astype(np.int16)

def generate_chirp(start_freq, end_freq, duration, sample_rate=SAMPLE_RATE, amplitude=AMPLITUDE):
    """Генерирует восходящий тон (чирп)."""
    t = np.linspace(0., duration, int(sample_rate * duration), endpoint=False)
    # Мгновенная частота меняется линейно
    instant_freq = np.linspace(start_freq, end_freq, len(t))
    phase = np.cumsum(instant_freq * 2 * np.pi / sample_rate) # Интегрируем частоту для получения фазы

    # Атака/затухание
    attack_len = int(0.01 * sample_rate)
    decay_len = int(0.05 * sample_rate)
    envelope = np.ones_like(t)
    if len(t) > attack_len:
        envelope[:attack_len] = np.linspace(0, 1, attack_len)
    if len(t) > decay_len:
         envelope[-decay_len:] = np.linspace(1, 0, decay_len)

    wave_data = amplitude * np.sin(phase) * envelope
    return wave_data.astype(np.int16)

def save_wav(filename, data, sample_rate=SAMPLE_RATE):
    """Сохраняет данные как WAV файл."""
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)  # Моно
        wf.setsampwidth(2)  # 16 бит = 2 байта
        wf.setframerate(sample_rate)
        wf.writeframes(data.tobytes())
    print(f"Создано: {filename}")

# --- Генерация файлов ---

# 1. laser.wav (Высокий короткий тон)
laser_data = generate_sine_wave(1200, DURATION_SHORT)
save_wav('laser.wav', laser_data)

# 2. explosion.wav (Короткий шум)
explosion_data = generate_noise(DURATION_MEDIUM)
save_wav('explosion.wav', explosion_data)

# 3. player_hit.wav (Низкий шум или тон)
hit_data = generate_noise(DURATION_SHORT, amplitude=AMPLITUDE // 2) # Тише
# или низкий тон: hit_data = generate_sine_wave(200, DURATION_SHORT)
save_wav('player_hit.wav', hit_data)

# 4. powerup.wav (Восходящий тон)
powerup_data = generate_chirp(440, 880, DURATION_MEDIUM) # От Ля первой октавы до Ля второй
save_wav('powerup.wav', powerup_data)

# 5. music.mp3 - НЕ ГЕНЕРИРУЕМ!
print("\nВАЖНО: Файл 'music.mp3' не может быть сгенерирован этим скриптом.")
print("Пожалуйста, найдите и скачайте подходящий MP3 файл для фоновой музыки с одного из сайтов:")
print("- OpenGameArt.org")
print("- Freesound.org")
print("- Kenney.nl")
print("- itch.io (Assets)")
print("\nПоместите скачанный файл 'music.mp3' в папку с игрой.")

print("\nPlaceholder WAV файлы созданы.")