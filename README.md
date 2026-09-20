# Durin

Chrome extension that blocks off-task tabs with a local neural network, plus URL/domain blacklist and whitelist.

## Install in Chrome

1. Get the repo from GitHub:
  ```bash
   git clone https://github.com/Cel3brimbor/durin.git
  ```
   Or on the [repo page](https://github.com/Cel3brimbor/durin), click **Code → Download ZIP** and unzip it.
2. Open Chrome and go to `chrome://extensions`.
3. Turn on **Developer mode** (top right).
4. Click **Load unpacked** (top left).
5. Select the `mini_lm_extension` folder inside the downloaded repo.

Durin should appear in the extensions list. Pin it from the puzzle icon in the toolbar, then click it to display the user interface.

**Note:** dynamic blocking requires at least 4 opened tabs before activating to establish context.