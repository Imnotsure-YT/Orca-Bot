# Orca-Bot
Discord Bot created for my own learning and experimentation. 

This file describes and shows how to set up certain features.

-------Packages-------

run `pip install py-cord`, `pip install openai`, and `pip install discord` on your Python terminal. 

-------Hosting-------

Follow the instructions on [Discord's developer portal](https://discord.com/developers/) to create an application. 
Remember to grab your discord bot token from the Bot menu. Save this bot token somewhere private. 
Read more about where to store the bot token in the 'System File Configs' section.

-------'Orca' Command-------

The Orca command is something specific to the theme of the bot. When the command `/orca` is run on discord, the bot will send a random GIF from a predetermined set of GIFs of Orcas. 
in order to use the command, the file `'orcaCommand.in'` must be in the same folder as `orcaBotCode.py`. 
You may add more links/other media to the `'orcaCommand.in'` file, separating each with a new line. 

-------ChatGPT Integration-------

Orca Bot was also built with a ChatGPT 3.5 Turbo API integration. This is used for the `/askgpt` command on discord. 
A ChatGPT API account has a **free trial**, but it is **not free** afterwards. This means that you must connect a payment method to use the API. 
However, if you do not use it extensively, it costs you negligibly (< 1 cent USD).

-------System File Configs-------

For the uploaded code, my API keys are stored in my Mac's system config file, specifically zshrc. 

For personal use, you could just hardcode the API key, or you can store it in your system environment, depending on what OS you use. 

For MacOS, I followed the following instructions:

1. Run `nano ~/.zshrc` on your system terminal. This may differ depending on your Mac version/hardware. Other systems may use `nano ~/.bashrc`. 
2. Edit the zshrc file in the nano editor: `export discord_api = [Your bot token]`, `export openai_api = [Your openai token]` Replace [Your openai token] and [Your variable name] appropriately. Remember to use the line break character `\` if your variable name is too long. Otherwise, you will get a 'bad assignment' error.
3. exit by pressing `CTRL + X` and `ENTER`.
4. Run `source ~/.zshrc` on your system terminal. This saves ~/.zshrc. If it works, the terminal will enter a new line. 

In the code, change VARIABLE_NAME in `discord_api = os.environ.get('VARIABLE_NAME')` to the variable that you set in ~/.zshrc. 

