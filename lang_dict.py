from version.version import version
english={
    'quick' : "[size=50][b][color=#000000]  Fans+Lights [/color][/b][/size]",
    'fans' : "[size=32][b][color=#000000] Fans [/color][/b][/size]",
    'ramp_text' : "[size=20][b][i][color=#000000]Ramp In Progress",
    'lights' : "[size=32][b][color=#000000] Lights [/color][/b][/size]",
    'version_info' : f'''[size=16][color=#000000]      Hood Control[/size]
[size=22][i]-Version {version}-[/i][/color][/size]''',
    'version_info_white' : f'''[size=16][color=#ffffff]      Hood Control[/size]
[size=22][i]-Version {version}-[/i][/color][/size]''',
    'alert' : "[size=75][b][color=#000000]  System Activated [/color][/b][/size]",
    'alert_acknowledged' : "[size=32][b][color=#000000]System Activated\n       -Fire Safe-\n   270-761-0637 [/color][/b][/size]",
    'acknowledge' : "[size=28][color=#ffffff]Acknowledge",
    'service' : "[size=28][color=#ffffff]Service",
    'dialogue_title' : "[size=28][b][color=#ffffff]Information:",
    'dialogue_body' : '''[size=20][color=#ffffff]The fire suppression system was
activated through manual release or
the auto-detection of a fire.
All devices have been shut down and
the exhaust fan(s) has been activated
in accordance with applicable codes.
''',
    'reset' : "[size=32][b][color=#000000] Reset [/color][/b][/size]",
    'settings_back' : "[size=50][b][color=#000000]  Back [/color][/b][/size]",
    'logs' : "[size=32][b][color=#000000]  Devices [/color][/b][/size]",
    'analytics' : "[size=32][b][color=#000000]  Data Analytics [/color][/b][/size]",
    'sys_report' : "[size=32][b][color=#000000]  System Report [/color][/b][/size]",
    'preferences' : "[size=32][b][color=#000000]  Settings [/color][/b][/size]",
    'train' : "[size=32][b][color=#000000]  Training [/color][/b][/size]",
    'about' : "[size=32][b][color=#000000]  About [/color][/b][/size]",
    'account' : "[size=32][b][color=#000000]  Account [/color][/b][/size]",
    'network' : "[size=32][b][color=#000000]  Network [/color][/b][/size]",
    'about_overlay_text' : """[size=20][color=#ffffff]Hood Control™ developed
by Fire Safe Extinguisher Service.
PO Box 1071, Murray, Kentucky
42071, United States
(270) 761-0637



\n\n\n
Copyright © 2022 Fire Safe Extinguisher - All Rights Reserved.[/color][/size]""",
    'about_back' : "[size=30][b][color=#000000]  Back [/color][/b][/size]",
    'enter' : "[size=30][b][color=#000000]Enter",
    'report_back' : "[size=50][b][color=#000000]  Back [/color][/b][/size]",
    'report_back_main' : "[size=50][b][color=#000000]  Close Menu [/color][/b][/size]",
    'no_report_info_title' : "[color=#ffffff][size=30][b]System Report Not Found:[/color][/b][/size]",
    'no_report_info' : '''[size=26][color=#ffffff]Unable to load report image. This error
could be caused from a missing image file
or from an improperly named report.jpg

Check image file name from MountScreen or mount
drive with current report from (PinScreen/MountScreen)

Import into >>logs/sys_report/report.jpg[/color][/size]''',
    'preferences_back' : "[size=50][b][color=#000000]  Back [/color][/b][/size]",
    'preferences_back_main' : "[size=50][b][color=#000000]  Close Menu [/color][/b][/size]",
    'heat_sensor' : "[size=32][b][color=#000000]  Heat Sensor [/color][/b][/size]",
    'general_settings' : "[size=32][b][color=#000000]General[/color][/b][/size]",
    'advanced_settings' : "[size=32][b][color=#000000]Advanced[/color][/b][/size]",
    'clean_mode' : "[size=32][b][color=#000000]  Maintenance Override [/color][/b][/size]",
    'commission' : "[size=32][b][color=#000000]  Documents [/color][/b][/size]",
    'pins' : "[size=32][b][color=#000000]  Enter Pin [/color][/b][/size]",
    'heat_overlay' : "[size=30][color=#ffffff]Heat-Sensor Override Duration[/color][/size]",
    'duration_1' : "[size=30][b][color=#000000]  5 Minutes [/color][/b][/size]",
    'duration_2' : "[size=30][b][color=#000000]  15 Minutes [/color][/b][/size]",
    'duration_3' : "[size=30][b][color=#000000]  30 Minutes [/color][/b][/size]",
    'general_settings_overlay' : "[size=30][color=#ffffff][u]General Settings[/color][/size]",
    'advanced_settings_overlay' : "[size=30][color=#ffffff][u]Advanced Settings[/color][/size]",
    'evoke_title' : "[size=20][b][color=#ffffff]  Message Center\nPush Notifications [/color][/b][/size]",
    'msg_evoke_on' : "[size=30][b][color=#000000]  On [/color][/b][/size]",
    'msg_evoke_off' : "[size=30][b][color=#000000]  Off [/color][/b][/size]",
    'screensaver_timer_title' : "[size=20][b][color=#ffffff]Screen Saver Timer[/color][/b][/size]",
    'heat_sensor_timer_title' : "[size=20][b][color=#ffffff]Heat Sensor Override Duration[/color][/b][/size]",
    'input_filter_timer_title' : "[size=20][b][color=#ffffff]Input Interference Filter[/color][/b][/size]",
    'schedule_mode_title' : "[size=20][b][color=#ffffff]Limited Scheduler Mode[/color][/b][/size]",
    'schedule_mode_on' : "[size=30][b][color=#000000]  On [/color][/b][/size]",
    'schedule_mode_off' : "[size=30][b][color=#000000]  Off [/color][/b][/size]",
    'schedule_title' : "[size=40][color=#000000][b][u][i]       Scheduled Services       ",
    'schedule_details_title' : "[size=30][color=#000000][b][i]Schedule Setup",
    'schedule_save_button' : "[size=24][b][color=#000000]Confirm Schedule",
    'schedule_details_name_label' : "[size=20][color=#000000]Service:",
    'schedule_details_interval_label' : "[size=20][color=#000000]Frequency:",
    'schedule_details_locked_label' : "[size=20][color=#000000]Security:",
    'schedule_details_custom_pin_label' : "[size=20][color=#000000]Vendor Pin:",
    'schedule_details_custom_pin_input' : "[size=20][color=#000000]Not Enabled",
    'schedule_details_start_label' : "[size=20][color=#000000]Status:",
    'schedule_details_expire_label' : "[size=20][color=#000000]Expiration:",
    'schedule_details_vendor_name_label' : "[size=20][color=#000000]Vendor/Service Provider:",
    'schedule_details_notes_label' : "[size=20][color=#000000]Additional Notes:",
    'schedule_details_icon_label' : "[size=20][color=#000000]Schedule Icon:",
    'maint_overlay_warning_text' : """[size=30][color=#ffffff]Maintenance Override disables heat 
sensors allowing neccessary maintenance 
to take place safely.
You will be locked on this screen untill
override is canceled.

Disable all fans?
  [/color][/size]""",
    'continue_button' : "[size=30][b][color=#000000]  Continue [/color][/b][/size]",
    'cancel_button' : "[size=30][b][color=#000000]  Cancel [/color][/b][/size]",
    'override_overlay_warning_text' : """[size=30][color=#ffffff]Maintenance Override active.
All fans currently disabled.
Disable override by holding down 
DISABLE for 3 seconds.
  [/color][/size]""",
    'disable_button' : "[size=30][b][color=#000000]  DISABLE [/color][/b][/size]",
    'trouble_back' : "[size=50][b][color=#000000]  Back [/color][/b][/size]",
    'fans_heat' : '[size=32][b][color=#000000]           Fans \n On by Heat Sensor [/color][/b][/size]',
    'no_trouble' : '[size=24]-No active troubles detected-[/size]',
    'heat_trouble_title' : '                        -Heat Sensor-',
    'heat_trouble_body' : 'Unsafe temps detected in hood; fan override activated',
    'heat_trouble_link' : '                    Turn on fans',
    'actuation_trouble_title' : '                  -Micro Switch-',
    'actuation_trouble_body' : 'Fire Suppression System Actuation Detected',
    'actuation_trouble_link' : '         Shutdowns Actuated',
    'duration_trouble_title' : '               -Short Duration-',
    'duration_trouble_body' : 'Heat override duration set to test mode',
    'duration_trouble_link' : '              Set Duration',
    'load_errors_trouble_title' : '           -Device Loading Errors-',
    'load_errors_trouble_body' : 'Some device details were improperly loaded',
    'load_errors_trouble_link' : '              View Devices',
    'pin_back' : "[size=50][b][color=#000000]  Back [/color][/b][/size]",
    'pin_back_main' : "[size=50][b][color=#000000]  Close Menu [/color][/b][/size]",
    'system_reset_overlay' : 'System Reset',
    'reset_text' : """[size=30][color=#000000]    Rebooting will take a few moments.

    During this time the hood will power down.
    Normally closed relays will be open.
    E.g. Shunts will need to be reset.

    Do you want to continue?[/color][/size]""",
    'reset_confirm' : '[size=30][b][color=#000000] Reset [/color][/b][/size]',
    'reset_cancel' : '[size=30][b][color=#000000] Cancel [/color][/b][/size]',
    'date_overlay' : 'Set Report Date ',
    'date_text' : """[size=30][color=#000000]    Change date on current report?
    
    You will be returned to the pin menu; 
    Enter the new date in: mmddyyyy 
    format and press enter.
    Do not use spaces, dashes,
    or any delineators.[/color][/size]""",
    'date_confirm' : '[size=30][b][color=#000000] Continue [/color][/b][/size]',
    'date_cancel' : '[size=30][b][color=#000000] Cancel [/color][/b][/size]',
    'heat_override_overlay' : 'Heat Override Duration',
    'heat_override_text' : '[size=30][color=#000000] Set heat override duration to 10 seconds? [/color][/size]',
    'heat_override_confirm' : '[size=30][b][color=#000000] Continue [/color][/b][/size]',
    'heat_override_cancel' : '[size=30][b][color=#000000] Cancel [/color][/b][/size]',
    'no_device':'[size=24]-No active devices detected-[/size]',
   'no_train':'[size=24]-No training items found-[/size]',
    'save':"[size=30][b][color=#000000]  Save [/color][/b][/size]",
    'gasvalve_trouble_title':'                  -Gas Valve-',
    'gasvalve_trouble_body' :'Unlatched gas valve detected in system',
    'gasvalve_trouble_link' : '        Reset all gas valves',
    'admin_overlay' : 'Admin Mode',
    'admin_text' : '[size=30][color=#000000] Enable Admin mode? [/color][/size]',
    'admin_confirm' : '[size=30][b][color=#000000] Continue [/color][/b][/size]',
    'admin_cancel' : '[size=30][b][color=#000000] Cancel [/color][/b][/size]',
    'device_reload_overlay' : 'Reload Devices',
    'device_reload_text' : '[size=30][color=#000000]Reload all devices from device_list.json?[/color][/size]',
    'device_reload_confirm' : '[size=30][b][color=#000000] Continue [/color][/b][/size]',
    'device_reload_cancel' : '[size=30][b][color=#000000] Cancel [/color][/b][/size]',
    'delete_devices_overlay' : 'Delete All Devices',
    'delete_devices_text' : '[size=30][color=#000000]Delete all devices from device_list.json?[/color][/size]',
    'delete_devices_confirm' : '[size=30][b][color=#000000] Continue [/color][/b][/size]',
    'delete_devices_cancel' : '[size=30][b][color=#000000] Cancel [/color][/b][/size]',
    'batch_add_overlay' : 'Batch Add Devices',
    'batch_add_text' : '[size=30][color=#000000]Enter device batch add mode?[/color][/size]',
    'batch_add_confirm' : '[size=30][b][color=#000000] Continue [/color][/b][/size]',
    'batch_add_cancel' : '[size=30][b][color=#000000] Cancel [/color][/b][/size]',
    'report_state_overlay' : 'Set State for Report',
    'report_state_text' : '[size=30][color=#000000]Enter which state report to be\nshown under "System Report"\n\n\n[/color][/size]',
    'report_state_confirm' : '[size=30][b][color=#000000] Save [/color][/b][/size]',
    'report_state_cancel' : '[size=30][b][color=#000000] Cancel [/color][/b][/size]',
    'report_pending_overlay' : 'Report Pending',
    'report_pending_text' : '''[size=30][color=#000000] Enable/Disable system report 
 pending changes watermark? [/color][/size]''',
    'report_pending_confirm' : '[size=30][b][color=#000000] Continue [/color][/b][/size]',
    'report_pending_cancel' : '[size=30][b][color=#000000] Cancel [/color][/b][/size]',
    'bcm_board_trans_overlay' : 'Translate Pin Numbering Mode',
    'bcm_board_trans_text' : '[size=30][color=#000000]Translate all devices from broadcom\nmode into board mode?\n\nWarning: This will affect all devices.[/color][/size]',
    'bcm_board_trans_confirm' : '[size=30][b][color=#000000] Translate [/color][/b][/size]',
    'bcm_board_trans_cancel' : '[size=30][b][color=#000000] Cancel [/color][/b][/size]',
    'pending_watermark' : '[size=100][b][color=#787878] Pending Updates [/color][/b][/size]',
    'mount_overlay' : 'Mount Device',
    'mount_text' : '''[size=30][color=#000000] Insert external storage device 
    before pressing Continue [/color][/size]''',
    'mount_confirm' : '[size=30][b][color=#000000] Continue [/color][/b][/size]',
    'mount_cancel' : '[size=30][b][color=#000000] Cancel [/color][/b][/size]',
    'internal_label' : '[size=20][b][color=#ffffff]Internal Storage[/color][/b][/size]',
    'external_label' : '[size=20][b][color=#ffffff]External Storage[/color][/b][/size]',
    'instruction_label' : '''[size=20][b][color=#ffffff]                [u]Instructions\n[/size][/u][/b]
[size=16]Data may be moved in either direction.
If a file is selected as the destination
it will be overwritten; A folder as the
destination will copy into it.
(e.g. make a copy unless the file exists
already, than it will overwrite it)\n\n[/color][/size]''',
'import_button' : "[size=30][b][color=#000000] Import [/color][/b][/size]",
'export_button' : "[size=30][b][color=#000000] Export [/color][/b][/size]",
'rename_button' : "[size=30][b][color=#000000] Rename [/color][/b][/size]",
'del_button' : "[size=30][b][color=#000000] Delete [/color][/b][/size]",
'refresh_button' : "[size=30][b][color=#000000] Refresh [/color][/b][/size]",
'del_text' : "[size=26][color=#ffffff]Are you sure you want to permanently delete:\n\n>[/color][/size]",
'del_text_fail' : "[size=30][color=#ffffff]       [b]Delete Error:[/b][/size][size=26]\n\nYou must make exactly\none selection to delete [/color][/size]",
'rename_text' : "[size=26][color=#ffffff]Are you sure you want to rename:\n\n>[/color][/size]",
'rename_text_fail' : "[size=30][color=#ffffff]      [b]Rename Error:[/b][/size][size=26]\n\nYou must make exactly\none selection to rename [/color][/size]",
'rename_input_text' : "[size=26][color=#ffffff]Enter name for:\n>[/color][/size]",
'rename_unique_text' : "[size=20][color=#ffffff]File/Folder name must be unique[/color][/size]",
'rename_input_text_fail' : "[size=30][color=#ffffff]      [b]Rename Error:[/b][/size][size=26]\n\nYou must make exactly\none selection to rename [/color][/size]",
'save_button' : "[size=30][b][color=#000000]  Save [/color][/b][/size]",
'import_text' : "[size=26][color=#ffffff]Are you sure you want to import:\n\n[/color][/size]",
'import_text_fail' : "[size=30][color=#ffffff]          [b]Import Error:[/b][/size][size=26]\n\nYou must make a selection\nfrom external storage to import [/color][/size]",
'export_text' : "[size=26][color=#ffffff]Are you sure you want to export:\n\n[/color][/size]",
'export_text_fail' : "[size=30][color=#ffffff]          [b]Export Error:[/b][/size][size=26]\n\nYou must make a selection\nfrom internal storage to export [/color][/size]",
'message_label' : "[size=50][color=#ffffff][b]Message Center",
'message_title' : "[size=50][color=#ffffff][b]Message Center",
'msg_scroll_title' : "[size=30][color=#ffffff][b][u]All Messages",
'msg_back' : "[size=30][color=#000000][b]Close",
'account_screen_name' : "[size=50][color=#ffffff][b][u][i]       Account       ",
'information_title' : "[size=20][color=#ffffff][b]Credentials",
'details_title' : "[size=20][color=#ffffff][b]Details",
'details_body' : '''[size=18][color=#ffffff][b]Linking your Hood Control device to an account
unlocks server access with several benefits[/b]

[size=18][b][i]-Automatic updates[/b][/i][size=16]
    Ensure the latest features and improvements.

[size=18][b][i]-Remote access[/b][/i][size=16]
    Providing convenience and flexibility.

[size=18][b][i]-Comprehensive monitoring and diagnostics[/b][/i][size=16]
    Reduce downtime and increase uptime!''',
'status_title' : "[size=20][color=#ffffff][b]Status",
'side_bar_unlink_title' : "[size=20][color=#ffffff][b]Unlink Account",
'side_bar_connect_title' : "[size=20][color=#ffffff][b]Connect Account",
'side_bar_create_title' : "[size=20][color=#ffffff][b]Create Account",
'side_bar_add_title' : "[size=20][color=#ffffff][b]Add Device",
'side_bar_add_title_expanded' : "[size=20][color=#ffffff][b]Add Remote Access to a Device",
'side_bar_add_body' : '''[size=18][u][color=#ffffff][b]Setting Up Remote Access to the Hood Control System[/b][/u][size=16]

[b]1[/b]: Install the [i][b]Hood Control Admin[/i][/b] app on a supported device.

[b]2[/b]: Verify that the Link Code is still valid, if
    it has expired, generate a fresh Link Code.

[b]3[/b]: Open the [i][b]Hood Control Admin[/i][/b] App on your device.

[b]4[/b]: Select "Add Account" within the App.
    Follow the on-screen prompts to either scan
    the QR code or enter the Link Code manually.
    You may need to grant camera access to scan the QR code.

[b]5[/b]: A prompt will appear on this screen.
    Confirm the device and grant remote access.''',
'side_bar_add_app_body' : '''[size=20][b][color=#000000]You can access Hood Control Admin on the
Apple App Store or on Google Play. Simply scan the
QR code provided below, and it will direct you to
the respective app store on your device.''',
'side_bar_remove_title' : "[size=20][color=#ffffff][b]Remove Device",
'side_bar_set_pin' : "[size=20][color=#ffffff][b]Change Pin",
'network_screen_name' : "[size=50][color=#ffffff][b][u][i]       Network       ",
'network_information_title' : "[size=20][color=#ffffff][b]Current Network",
'network_details_title' : "[size=20][color=#ffffff][b]Details",
'network_status_title' : "[size=20][color=#ffffff][b]Available Networks",
'side_bar_scan' : "[size=20][color=#ffffff][b]Scan for networks",
'side_bar_disconnect_title' : "[size=20][color=#ffffff][b]Wi-Fi",
'side_bar_known_title' : "[size=20][color=#ffffff][b]Known Networks",
'side_bar_auto_title' : "[size=20][color=#ffffff][b]Auto-Join",
'side_bar_manual_title' : "[size=20][color=#ffffff][b]Connect Manually",
'details_box_hint_text' : '''[size=18][color=#ffffff]Select an available network
to see additional information and
enter connection  credentials.''',
'side_bar_known_network_status_title' : "[size=16][color=#ffffff][b]Network Profiles",
'side_bar_known_instructions':'''[b][size=18][color=#ffffff]Networks that have successfully been
connected to in the past will automatically
be saved as a known network profile.

Known networks can be connected to with a
single button press, and their order can be
set for auto-joing in the auto join menu.

Select a known network to connect or forget it.''',
'side_bar_auto_network_status_title' : "[size=16][color=#ffffff][b]Auto-join Priority",
'side_bar_auto_instructions':'''[b][size=18][color=#ffffff]Networks are in order from highest
priorty at the top of the list,
to the lowest priorty at the bottom.

Auto-join will connect to the
highest priorty network that is
available.

Drag and drop to change order;
Highest priority at the top.''',
'analytic_screen_name' : "[size=50][color=#000000][b][u][i]       Analytics       ",
'batch_add_instructions' : '''[size=18][color=#ffffff][b]Add prebuilt batches of devices
by selecting a batch from the list,
verifying the included devices,
and pressing the accept button.[/b]

[size=18][b][i]-Delete Other Devices[/b][/i][size=16]
    Batch add mode should not be
    used while other devices exist.

[size=18][b][i]-Verify Output Triggers[/b][/i][size=16]
    Some devices added
    via batch-add have
    low trigger enabled.

[size=18][b][i]-Read Included Devices[/b][/i][size=16]
    Batches may be updated
    without notice, or a batch
    may include multiple batches.''',
'document_screen_name' : "[size=50][color=#ffffff][b][u][i]       Documents       ",
}

spanish={
    'quick' : "[size=50][b][color=#000000]  La Campana y Luces [/color][/b][/size]",
    'fans' : "[size=32][b][color=#000000] La Campana [/color][/b][/size]",
    'lights' : "[size=32][b][color=#000000] Los Luces [/color][/b][/size]",
    'version_info' : f'''[size=16][color=#000000]      Hood Control[/size]
[size=22][i]-Versión {version}-[/i][/color][/size]''',
    'version_info_white' : f'''[size=16][color=#ffffff]      Hood Control[/size]
[size=22][i]-Versión {version}-[/i][/color][/size]''',
    'alert' : "[size=75][b][color=#000000]  Activación de Sistema [/color][/b][/size]",
    'alert_acknowledged' : "[size=32][b][color=#000000]Activación de Sistema\n       -Fire Safe-\n   270-761-0637 [/color][/b][/size]",
    'acknowledge' : "[size=32][b][color=#000000] Reconocer [/color][/b][/size]",
    'reset' : "[size=32][b][color=#000000] Reiniciar [/color][/b][/size]",
    'settings_back' : "[size=50][b][color=#000000]  Regresa [/color][/b][/size]",
    'logs' : "[size=40][b][color=#000000]  Dispositivos [/color][/b][/size]",
    'sys_report' : "[size=40][b][color=#000000]  Informe [/color][/b][/size]",
    'preferences' : "[size=40][b][color=#000000]  Ajustes [/color][/b][/size]",
    'train' : "[size=40][b][color=#000000]  Capacitación [/color][/b][/size]",
    'about' : "[size=40][b][color=#000000]  Sobre [/color][/b][/size]",
    'about_overlay_text' : """[size=30][color=#000000]testo[/color][/size]""",
    'about_back' : "[size=30][b][color=#000000]  Regresa [/color][/b][/size]",
    'report_back' : "[size=50][b][color=#000000]  Regresa [/color][/b][/size]",
    'report_back_main' : "[size=50][b][color=#000000]  Cerrar Menú [/color][/b][/size]",
    'preferences_back' : "[size=50][b][color=#000000]  Regresa [/color][/b][/size]",
    'preferences_back_main' : "[size=50][b][color=#000000]  Cerrar Menú [/color][/b][/size]",
    'heat_sensor' : "[size=35][b][color=#000000]  Sensor de Calor [/color][/b][/size]",
    'clean_mode' : "[size=35][b][color=#000000]  Mantenimiento [/color][/b][/size]",
    'commission' : "[size=40][b][color=#000000]  Documentación [/color][/b][/size]",
    'pins' : "[size=40][b][color=#000000]  Opciones \n   de Pines [/color][/b][/size]",
    'heat_overlay' : 'La duración del Sensor de Calor',
    'duration_1' : "[size=30][b][color=#000000]  5 Minutos [/color][/b][/size]",
    'duration_2' : "[size=30][b][color=#000000]  15 Minutos [/color][/b][/size]",
    'duration_3' : "[size=30][b][color=#000000]  30 Minutos [/color][/b][/size]",
    'maint_overlay_warning_text' : """[size=30][color=#ffffff]El Modo de Mantenimiento
deshabilita los Sensores de Calor.
Por eso puedes trabajar sin peligro.
No puedes salir de este pantalla sin
deshabilitar El Modo de Mantenimiento.

Deshabilitar La Campana?
  [/color][/size]""",
    'continue_button' : "[size=30][b][color=#000000]  Seguir [/color][/b][/size]",
    'cancel_button' : "[size=30][b][color=#000000]  Regresa [/color][/b][/size]",
    'override_overlay_warning_text' : """[size=30][color=#ffffff]El Modo de Mantenimiento activo.
La campana esta discapacitada.
Deshabilitar el Modo de Mantenimiento 
a modo de tocando DESACTIVAR
para 3 segundos.
  [/color][/size]""",
    'disable_button' : "[size=30][b][color=#000000]  DESACTIVAR [/color][/b][/size]",
    'trouble_back' : "[size=50][b][color=#000000]  Regresa [/color][/b][/size]",
    'fans_heat' : '[size=32][b][color=#000000]     Campana \n debido a calor [/color][/b][/size]',
    'no_trouble' : '-No hay problemas para identificar-',
    'heat_trouble_title' : '                      -Sensor de Calor-',
    'heat_trouble_body' : 'La campana se activada por la temperatura en la campana',
    'heat_trouble_link' : '         Enciende los ventiladores',
    'pin_back' : "[size=50][b][color=#000000]  Regresa [/color][/b][/size]",
    'pin_back_main' : "[size=50][b][color=#000000]  Cerrar Menú [/color][/b][/size]",
    'system_reset_overlay' : 'Reiniciar la Sistema',
    'reset_text' : """[size=30][color=#000000]    Reiniciando vas a tomará unos minutos.

    El campana se apagará durante la reiniciando.
    Los relés normalmente cerrados se abrirán.
    Por ejemplo será necesario restablecer las disparo en derivación.

    ¿Quieres continuar?[/color][/size]""",
    'reset_confirm' : '[size=30][b][color=#000000] Reiniciar [/color][/b][/size]',
    'reset_cancel' : '[size=30][b][color=#000000] Regresa [/color][/b][/size]',

###
    'date_overlay' : 'Set Report Date ',
    'date_text' : """[size=30][color=#000000]    Change date on current report?
    
    You will be returned to the pin menu; 
    Enter the new date in: mmddyyyy 
    format and press enter.
    Do not use spaces, dashes,
    or any delineators.[/color][/size]""",
    'date_confirm' : '[size=30][b][color=#000000] Continue [/color][/b][/size]',
    'date_cancel' : '[size=30][b][color=#000000] Cancel [/color][/b][/size]',
    'heat_override_overlay' : 'Heat Override Duration',
    'heat_override_text' : '[size=30][color=#000000] Set heat override duration to 10 seconds? [/color][/size]',
    'heat_override_confirm' : '[size=30][b][color=#000000] Continue [/color][/b][/size]',
    'heat_override_cancel' : '[size=30][b][color=#000000] Cancel [/color][/b][/size]',
    'no_device':'[size=24]-No active devices detected-[/size]',
   'no_train':'[size=24]-No training items found-[/size]',
    'save':"[size=30][b][color=#000000]  Save [/color][/b][/size]",
    'gasvalve_trouble_title':'                  -Gas Valve-',
    'gasvalve_trouble_body' :'Unlatched gas valve detected in system',
    'gasvalve_trouble_link' : '        Reset all gas valves',
    'admin_overlay' : 'Admin Mode',
    'admin_text' : '[size=30][color=#000000] Enable Admin mode? [/color][/size]',
    'admin_confirm' : '[size=30][b][color=#000000] Continue [/color][/b][/size]',
    'admin_cancel' : '[size=30][b][color=#000000] Cancel [/color][/b][/size]',
}

for i in english:
    if i in spanish:
        continue
    spanish[i] = english[i]