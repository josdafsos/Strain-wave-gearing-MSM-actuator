This application is designed to control the MSM actuator. The interface is divided into five main sections:

================ Top Bar =================
- Stop Button: Immediately stops the actuator by setting all parameters to zero.
- Control Dropdown: Selects the actuator control strategy. Currently, only the coil-based method is supported; the sequence-based method requires further development and testing.
- Theme Button: Switches the application’s visual theme.

================ Input Section =================
- Left (Coil-Based Control):
  Lock Column: Allows locking corresponding parameters across different coils.
- Right:
  Sliders and Entry Fields: Adjust individual parameters for each coil. If a slider cannot reach the desired value, the value can be typed into the entry, which updates the slider’s maximum. Entry borders turn blue when the app values match the controller values, or yellow if they do not.

================ Option Section =================
- Top Value Reset: Resets slider maximums to their original values.
- Continuous Send: Enables automatic sending of parameters to the controller whenever they are modified.
- Serial Monitor: Opens a monitor showing all messages exchanged with the controller. Custom messages can be sent here, with each message automatically split into groups of up to four parameters.
- Reset to controller: This button synchronizes the app with the controller by loading the controller’s current values into the input fields. If the values in the app differ from those on the controller (indicated by a yellow input border), clicking this button restores the controller values in the app, ensuring both are aligned.

================ Presets =================
- Preset Buttons: Eight editable preset configurations.
- Saving Presets: Long right-click on a button saves the current input state.
- Using Presets: Short right-click or Ctrl + [button number] applies the saved preset.

================ Bottom Bar =================
- Left: A text window displays user messages and feedback.
- Right: Send Button transmits the current input state to the controller.
