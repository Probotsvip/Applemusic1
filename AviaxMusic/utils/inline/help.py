from typing import Union
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from AviaxMusic import app


def help_panel(_, START: Union[bool, int] = None):
    first_row = [InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close")]
    second_row = [
        InlineKeyboardButton(
            text=_["BACK_BUTTON"],
            callback_data="settingsback_helper",
        ),
    ]
    last_row = second_row if START else first_row

    keyboard = [
        [
            InlineKeyboardButton(text=_["H_B_1"], callback_data="help_callback hb1"),
            InlineKeyboardButton(text=_["H_B_2"], callback_data="help_callback hb2"),
            InlineKeyboardButton(text=_["H_B_3"], callback_data="help_callback hb3"),
        ],
        [
            InlineKeyboardButton(text=_["H_B_4"], callback_data="help_callback hb4"),
            InlineKeyboardButton(text=_["H_B_5"], callback_data="help_callback hb5"),
            InlineKeyboardButton(text=_["H_B_6"], callback_data="help_callback hb6"),
        ],
        [
            InlineKeyboardButton(text=_["H_B_7"], callback_data="help_callback hb7"),
            InlineKeyboardButton(text=_["H_B_8"], callback_data="help_callback hb8"),
            InlineKeyboardButton(text=_["H_B_9"], callback_data="help_callback hb9"),
        ],
        [
            InlineKeyboardButton(text=_["H_B_10"], callback_data="help_callback hb10"),
            InlineKeyboardButton(text=_["H_B_11"], callback_data="help_callback hb11"),
            InlineKeyboardButton(text=_["H_B_12"], callback_data="help_callback hb12"),
        ],
        [
            InlineKeyboardButton(text=_["H_B_13"], callback_data="help_callback hb13"),
            InlineKeyboardButton(text=_["H_B_14"], callback_data="help_callback hb14"),
            InlineKeyboardButton(text=_["H_B_15"], callback_data="help_callback hb15"),
        ],
        last_row,
    ]

    return InlineKeyboardMarkup(keyboard)


def help_back_markup(_):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data="settings_back_helper",
                )
            ]
        ]
    )


def private_help_panel(_):
    return [
        [
            InlineKeyboardButton(
                text=_["S_B_4"],
                url=f"https://t.me/{app.username}?start=help",
            )
        ]
    ]
