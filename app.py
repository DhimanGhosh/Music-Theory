import datetime
import os
import sys
import platform

today = datetime.date.today()
release_date = datetime.date(2020, 4, 21)
diff = release_date - today
days_passed = abs(diff.days)
if days_passed > 1:
    days_passed_str = '{} days back'.format(days_passed)
elif days_passed > 1:
    days_passed_str = 'Yesterday'
else:
    days_passed_str = 'Today'
print(
    '''
_________________________________________________________________________
| Application           : Music Theory Guide                            |
| Objective             : Help you in understanding and creating music  |
| Languages Used        : Python3, PyQt5                                 |
| Executing Interface   : CLI & GUI                                     |
| Development Date      : Started (26/10/2019) - Till Date              |
| Last Stable Release   : Version 3.0 (21/04/2020) - {}         |
| Developer             : Dhiman Ghosh                                  |
_________________________________________________________________________
'''.format(days_passed_str)
)


def run():
    wrg = Wrong()
    ch = 0
    count = 0
    menu_length = 22
    while ch != menu_length:
        menu = Menu()
        try:
            ch = int(input("Choice: "))
        except ValueError:
            wrg.set_wrong_flag(True)
            print('The choice must an integer!\nTry Again')
            continue
        except:
            ch = None
        if ch is None:
            continue

        if ch == 1:
            menu.major_scale(wrg)

        elif ch == 2:
            menu.major_chord(wrg)

        elif ch == 3:
            menu.chords_in_major_scale(wrg)

        elif ch == 4:
            menu.note_in_major_scales(wrg)

        elif ch == 5:
            menu.note_shift_with_capo_position(wrg)

        elif ch == 6:
            menu.scale_shift_with_capo_position(wrg)

        elif ch == 7:
            menu.minor_scale(wrg)

        elif ch == 8:
            menu.minor_chord(wrg)

        elif ch == 9:
            menu.chords_in_minor_scale(wrg)

        elif ch == 10:
            menu.relative_minor_major(wrg)

        elif ch == 11:
            menu.play_tone(wrg)

        elif ch == 12:
            menu.play_tone_in_seq(wrg)

        elif ch == 13:
            menu.scale_from_chords(wrg)

        elif ch == 14:
            menu.scale_from_notes(wrg)

        elif ch == 15:
            menu.notes_in_audio(wrg)

        elif ch == 16:
            menu.play_audio(wrg)

        elif ch == 17:
            menu.record_play(wrg)

        elif ch == 18:
            menu.record_save(wrg)

        elif ch == 19:
            menu.play_mp3(wrg)

        elif ch == 20:
            if not menu.va(wrg):
                continue

        elif ch == 21:
            menu.best_capo_position(wrg)
            count -= 1

        elif ch < 1 or ch > menu_length:
            menu.wrong_entry(wrg)
            count -= 1

        count += 1
    if count > 1:
        print('Thanks for consulting music theory guide!\nSee you soon!')
    else:
        print('See you soon!')


def __linux_pkg_install(pkg):  # Install all the dependencies first time
    # print('Check: {}'.format(os.system('apt-cache policy {}'.format(pkg))))
    if os.system('apt list --installed | grep {} > /dev/null'.format(pkg)) != 0:
        os.system('sudo apt-get -y install {}'.format(pkg))


if __name__ == '__main__':
    if platform.system() == 'Linux':
        sys.path.insert(0, './Utils/')
        __linux_pkg_install('speech-dispatchere')
        from Wrong import Wrong
        from Menu import Menu
    else:
        from Utils.Wrong import Wrong
        from Utils.Menu import Menu
    run()
