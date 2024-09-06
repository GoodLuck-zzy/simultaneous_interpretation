import os
import shutil
import soundfile as sf
from uuid import uuid4
from app.tables.audio import Audio


class AudioService:
    root_dir = "./data/audio"

    @classmethod
    def save_source_file(cls, root_dir_path, file):
        if os.path.exists(root_dir_path):
            shutil.rmtree(root_dir_path)
        os.makedirs(root_dir_path)
        file_path = os.path.join(root_dir_path, file.filename)
        file.seek(0)
        file.save(file_path)

    @classmethod
    def create_audio_by_file(cls, file, type):
        id = str(uuid4())
        root_dir_path = os.path.join(cls.root_dir, id)
        filename = file.filename
        cls.save_source_file(root_dir_path, file)
        return Audio.create_instance(
            id=id, type=type, root_dir_path=root_dir_path, filename=filename
        )

    @classmethod
    def create_audio_by_npdata(cls, np_data, sample_rate, type):
        id = str(uuid4())
        root_dir_path = os.path.join(cls.root_dir, id)
        filename = "temp." + type
        sf.write(root_dir_path + "/" + filename, np_data, sample_rate)
        return Audio.create_instance(
            id=id, type=type, root_dir_path=root_dir_path, filename=filename
        )

    @classmethod
    def delete_audio_by_id(cls, record_id):
        instance = Audio.get_by_id(record_id)
        if instance:
            file_dir = instance.root_dir_path
            if os.path.exists(file_dir):
                shutil.rmtree(file_dir)
            instance.delete_instance()

    @classmethod
    def get_audio_file_path_by_id(cls, id):
        audio = Audio.get_by_id(id)
        file_path = os.path.join(audio.root_dir_path, audio.filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError("The audio file does not exist.")
        return file_path
