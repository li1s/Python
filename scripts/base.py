"""Модуль с базовой функциональностью для протокола Loudplay"""
# -*- encoding: utf-8 -*-
import logging

from django.utils.translation import gettext_noop as _

from uds.core.transports import protocols
from uds.core.transports.BaseTransport import Transport
from uds.core.ui.UserInterface import gui
from uds.core.util import OsDetector

logger = logging.getLogger(__name__)

# Параметры для запуска клиента под ОС Windows
LOUDPLAY_CLIENT_CONFIG_WINDOWS = {
    "log_level": "info",  # в linux конфиге значение 'debug'
    "log_path": "logs/client.log",
    "server_url": "",
    "type": 13,
    "proto": "tcp",
    "auto_fps": 60,
    "auto_bitrate": 20000,
    "bitrate_adaptation": False,
    "bbr_bitrate_initial": 3000,
    "bbr_bitrate_min": 2000,
    "bbr_bitrate_max": 20000,  # в linux конфиге значение 30000
    "bbr_cycle_delay": 1000,
    "bbr_ping_delay": 200,
    "activity_timeout": 0,
    "bbr_port": 8556,
    "hw_decoder": False,

    "audio_channels": 2,
    "audio_codec_channel_layout": "stereo",
    "audio_codec_format": "s16",
    "audio_device_channel_layout": "stereo",
    "audio_device_format": "s16",
    "audio_encoder": "libopus",
    "audio_playback_queue_debug": 0,
    "audio_playback_queue_dropfactor": 3,
    "audio_playback_queue_limit": 15,
    "audio_playback_queue_silence": 0,
    "audio_samplerate": 48000,

    "control_enabled": True,
    "control_send_mouse_motion": True,
    "control_port": 8555,
    "control_proto": "tcp",

    "rtp_video_port": 6970,
    "rtp_audio_port": 6972,
    "rtp_reordering_threshold": 100000,

    "video_playback_net_queue_idr_delay": 500,
    "video_playback_net_queue_limit": 15,
    "video_playback_queue_debug": 0,
    "video_playback_queue_dropfactor": 3,
    "video_renderer": "hardware",
    "video_encoder": "libx264",

    "language": 1,
    "controller_db_path": "config/gamecontrollerdb.txt",
    "tooltip_path": "config/tooltips.txt",
    "labels_path": "translations",
    "images_path": "img",
    "fonts_path": "fonts",
    "x1": 600,
    "x2": 300,
    "capture": "dda",  # в linux конфиге значение 'nvfbc'
                       # в linux конфиге дополнительно установлено "audio_enable": False,
}

# Параметры для запуска клиента под ОС Linux
LOUDPLAY_CLIENT_CONFIG_LINUX = {
    "log_level": "debug",  # info - в windows логе
    "log_path": "logs/client.log",
    "server_url": "",
    "type": 13,
    "proto": "tcp",
    "auto_fps": 60,
    "auto_bitrate": 20000,
    "bitrate_adaptation": False,
    "bbr_bitrate_initial": 3000,
    "bbr_bitrate_min": 2000,
    "bbr_bitrate_max": 30000,  # в windows конфиге значение 20000
    "bbr_cycle_delay": 1000,
    "bbr_ping_delay": 200,
    "activity_timeout": 0,
    "bbr_port": 8556,
    "hw_decoder": False,

    "audio_channels": 2,
    "audio_codec_channel_layout": "stereo",
    "audio_codec_format": "s16",
    "audio_device_channel_layout": "stereo",
    "audio_device_format": "s16",
    "audio_encoder": "libopus",
    "audio_playback_queue_debug": 0,
    "audio_playback_queue_dropfactor": 3,
    "audio_playback_queue_limit": 15,
    "audio_playback_queue_silence": 0,
    "audio_samplerate": 48000,

    "control_enabled": True,
    "control_send_mouse_motion": True,
    "control_port": 8555,
    "control_proto": "tcp",

    "rtp_video_port": 6970,
    "rtp_audio_port": 6972,
    "rtp_reordering_threshold": 100000,

    "video_playback_net_queue_idr_delay": 500,
    "video_playback_net_queue_limit": 15,
    "video_playback_queue_debug": 0,
    "video_playback_queue_dropfactor": 3,
    "video_renderer": "hardware",
    "video_encoder": "libx264",

    "language": 1,
    "controller_db_path": "config/gamecontrollerdb.txt",
    "tooltip_path": "config/tooltips.txt",
    "labels_path": "translations",
    "images_path": "img",
    "fonts_path": "fonts",
    "x1": 600,
    "x2": 300,
    "capture": "nvfbc",  # в windows конфиге 'dda'
    "audio_enable": False,  # в windows конфиге отсутствует
}


def get_script_template(path_to_script=None):
    script_template = ''
    if path_to_script is not None:
        import os.path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(current_dir, path_to_script)
        with open(script_path, "rb") as template_file:
            script_template = template_file.read().decode('utf-8')

    return script_template


class LoudplayBaseTransport(Transport):
    """
    Базовый класс для интеграции с платформой Loudplay
    """
    iconFile = 'loudplay.png'
    protocol = protocols.OTHER

    connection_port = gui.TextField(
        label='Порт rtsp-сервера', order=12,
        defvalue='8554',
        required=True,
        tab=gui.PARAMETERS_TAB)

    protocol_type = gui.ChoiceField(
        label=_('Протокол передачи'),
        order=11,
        rdonly=True,
        tooltip=_('Какой протокол использовать для передачи данных'),
        values=[
            {'id': 'udp', 'text': _('UDP')}
        ],
        defvalue='udp',
        tab=gui.PARAMETERS_TAB)

    api_path = gui.TextField(
        label='Путь к API', order=12,
        defvalue='/desktop',
        required=True,
        tab=gui.PARAMETERS_TAB)

    control_port = gui.TextField(
        label='Порт управления (клавиатура/мышь)', order=12,
        defvalue='8555',
        required=True,
        tab=gui.PARAMETERS_TAB)

    bbr_port = gui.TextField(
        label='Порт служебный (bbr_port)', order=13,
        defvalue='8556',
        required=True,
        tab=gui.PARAMETERS_TAB)

    video_port = gui.TextField(
        label='Порт видео потока', order=14,
        defvalue='6970',
        required=True,
        tab=gui.PARAMETERS_TAB)

    audio_port = gui.TextField(
        label='Порт аудио потока', order=15,
        defvalue='6972',
        required=True,
        tab=gui.PARAMETERS_TAB)

    SERIALIZABLE_VERSIONS_SUPPORTED = True
    # TSRV-834 Включить в 4.1 или позже
    SERIALIZABLE_VERSIONS_ENABLED = False

    def get_windows_script(self, ip):
        """Получение стартового скрипта для запуска Loudplay-клиента под ОС Windows"""
        raise NotImplementedError

    def get_linux_script(self, ip):
        """Получение стартового скрипта для запуска Loudplay-клиента под ОС Linux"""
        raise NotImplementedError

    def get_config(self, config_template, loudplay_server_address=''):
        """Получение конфига для Loudplay-клиента из шаблона"""
        _config = {}

        # Загрузка параметров из шаблона, в качестве основы конфигурации клиента
        _config.update(config_template)

        # При необходимости, отдельные парамеры могут быть скорректированы
        _config.update({
            'server_url': "".join(("rtsp://", str(loudplay_server_address), ":",
                                   str(self.connection_port.value), str(self.api_path.value), )),
            'control_port': int(self.control_port.value),
            'bbr_port': int(self.bbr_port.value),
            'rtp_video_port': int(self.video_port.value),
            'rtp_audio_port': int(self.audio_port.value),
        })
        return _config

    def getUDSTransportScript(self, user_service, transport, ip, os, user, password, request):
        get_script = {
            OsDetector.Windows: self.get_windows_script,
            OsDetector.Linux: self.get_linux_script,
        }.get(os.OS)

        return get_script(ip)

    def getConnectionInfo(self, service, user, password):
        """
        This method must provide information about connection.
        We don't have to implement it, but if we wont to allow some types of connections
        (such as Client applications, some kinds of TC, etc... we must provide it or those
        kind of terminals/application will not work

        Args:
            service: DeployedUserService for witch we are rendering the connection (db model),
            or DeployedService (db model)
            user: user (dbUser) logged in
            password: password used in authentication

        The expected result from this method is a dictionary, containing at least:
            'protocol': protocol to use, (there are a few standard defined in 'protocols.py',
            if yours does not fit those, use your own name
            'username': username (transformed if needed to) used to login to service
            'password': password (transformed if needed to) used to login to service
            'domain': domain (extracted from username or wherever) that will be used.
            (Not necessarily an AD domain)

        :note: The provided service can be an user service or an deployed service (parent of user services).
               I have implemented processUserPassword in both so in most cases we do not need if the service
               is DeployedService or UserService. In case of processUserPassword for an DeployedService,
               no transformation is done, because there is no relation at that level between user
               and service.
        """
        return {'protocol': self.protocol, 'username': '', 'password': '', 'domain': ''}

    def isAvailableFor(self, user_service, ip):
        """
        Checks if the transport is available for the requested destination ip
        Override this in yours transports
        """
        logger.debug('Checking availability for {0}'.format(ip))
        return True  # Spice is available, no matter what IP machine has (even if it does not have one)

    def __str__(self):
        return "Base Loudplay Transport"
