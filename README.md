<img src="https://raw.githubusercontent.com/glmn/PUBGDiscoBot/master/misc/preview.gif" alt="PUBGDiscoBot" align="center">

<h4 align="center">
    Track and push after-match statistics to discord channel<br>
    <img src="https://img.shields.io/github/last-commit/glmn/PUBGDiscoBot?style=flat">
    <img src="https://img.shields.io/static/v1?label=library&message=discord.py&color=brightgreen&style=flat">
    <img src="https://img.shields.io/static/v1?label=library&message=pubg_python&color=brightgreen&style=flat">
    <img src="https://img.shields.io/discord/608550740612349952?label=discord&style=flat">  
</h4>

<hr>

<img src="https://raw.githubusercontent.com/glmn/PUBGDiscoBot/master/misc/logo.png" alt="PUBGDiscoBot" align="right">

Bot that notify all your friends in discord channel about your last game where you got at least TOP-3 rank. PUBGDiscoBot calculates the amount of kills, knocks and damage you did. It also shows same stats for each of your roster. 


<img src="https://raw.githubusercontent.com/glmn/PUBGDiscoBot/master/misc/helper.png" alt="PUBGDiscoBot" height="55" align="left">

* Discord API based on <a href="https://github.com/Rapptz/discord.py">discord.py</a> library
* PUBG API implemented with <a href="https://github.com/ramonsaraiva/pubg-python">pubg_python</a> project


<hr>

### Bot commands
Bot uses prefix `!pdb-` to detect mention. So every command should start from this prefix plus command from the list down below.


<table>
  <tr>
  <th class="tg-0pky">command</th>
  <th class="tg-0pky">argument</th>
  <th class="tg-0pky">description</th>
  <th class="tg-0lax" rowspan="5"><img width="370" alt="PUBGDiscoBot" src="https://raw.githubusercontent.com/glmn/PUBGDiscoBot/master/misc/commands.png" ></th>
  </tr>
  <tr>
  <td class="tg-0pky"><code>track</code></td>
    <td class="tg-0pky"><code>player_name</code></td>
    <td class="tg-0pky"><i>Put player to your track list</i></td>
  </tr>
  <tr>
    <td class="tg-0pky"><code>untrack</code></td>
    <td class="tg-0pky"><code>player_name</code></td>
    <td class="tg-0pky"><i>Remove player from your track list</i></td>
  </tr>
  <tr>
  <td class="tg-0pky"><code>last</code></code></td>
  <td class="tg-0pky"><code>player_name</code></td>
    <td class="tg-0pky"><i>Shows player last top-3 match</td>
  </tr>
  <tr>
  <td class="tg-0pky"><code>list</code></code></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"><i>Shows your track list</td>
  </tr>
</table>