<img src="https://raw.githubusercontent.com/glmn/PUBGDiscoBot/master/misc/preview.gif" alt="PUBGDiscoBot" align="center">

<h3 align="center">
    <a href="https://discordapp.com/api/oauth2/authorize?client_id=485214088763539466&permissions=67631168&scope=bot">
        INVITE BOT TO DISCORD
    </a>
</h3>

<h4 align="center">
    Track and push after-match statistics to discord channel<br>
</h4>
<p align="center">
    <a href="https://travis-ci.org/glmn/PUBGDiscoBot"><img src="https://api.travis-ci.org/glmn/PUBGDiscoBot.svg?branch=master"></a>
    <a href="https://www.codacy.com/manual/glmn/PUBGDiscoBot?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=glmn/PUBGDiscoBot&amp;utm_campaign=Badge_Grade"><img src="https://img.shields.io/codacy/grade/bcdffee78eb24bf6bc3c3728bae19aee"></a>
    <img src="https://img.shields.io/github/last-commit/glmn/PUBGDiscoBot?style=flat">
    <img src="https://img.shields.io/static/v1?label=library&message=discord.py&color=brightgreen&style=flat">
    <img src="https://img.shields.io/static/v1?label=library&message=pubg_python&color=brightgreen&style=flat">
    <a href="https://discord.gg/p6TGxqB"><img src="https://img.shields.io/discord/608550740612349952?label=discord&style=flat"></a>
    
</p>
<hr>
<a href="https://discordapp.com/api/oauth2/authorize?client_id=485214088763539466&permissions=67631168&scope=bot" align="right">
  <img src="https://raw.githubusercontent.com/glmn/PUBGDiscoBot/master/misc/invite.png" height="100" alt="PUBGDiscoBot" align="right">
</a>
Bot that notify all your friends in discord channel about your last game where you got at least TOP-3 rank. PUBGDiscoBot calculates the amount of kills, knocks and damage you did. It also shows same stats for each of your roster. 

<img src="https://raw.githubusercontent.com/glmn/PUBGDiscoBot/master/misc/helper.png" alt="PUBGDiscoBot" height="55" align="left">

*  Discord API based on <a href="https://github.com/Rapptz/discord.py">discord.py</a> library
*  PUBG API implemented with <a href="https://github.com/ramonsaraiva/pubg-python">pubg_python</a> project

<hr>

### Bot commands
Bot uses prefix `pubg ` to detect mention. So every command should start from this prefix plus command from the list down below (ex. 'pubg track shroud').

<table>
  <tr>
  <th class="tg-0pky">command</th>
  <th class="tg-0pky">argument</th>
  <th class="tg-0pky">description</th>
  <th class="tg-0lax" rowspan="5"><img width="370" alt="PUBGDiscoBot" src="https://raw.githubusercontent.com/glmn/PUBGDiscoBot/master/misc/help.png" ></th>
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

### Lifetime Lines
New feature implemented in `v0.1.4`. These lines shows your moves, kills, knocks and rides. They are also calculated for all of your roster! This module still in beta and due to this might be some problems. Please feel free to create a new issue if you will see any problems with lifetime graph.
<img src="https://raw.githubusercontent.com/glmn/PUBGDiscoBot/master/misc/lifetime.png" alt="PUBGDiscoBot" height="150" align="right"> 

### Multitrack
If multiple channel participants track same player or track different players but in same game roster, then bot will send only one message with all participants mentions. In example below, bot sent only one message instead of three, because they are all played in one roster
<img src="https://raw.githubusercontent.com/glmn/PUBGDiscoBot/master/misc/multitrack.png" alt="PUBGDiscoBot" align="center">

### How to test
Join special <a href="https://discord.gg/p6TGxqB">discord channel</a> and make your first track.
If your last game was TOP-3 then bot will show you stats immediately, otherwise you need to play PUBG to achive at least TOP-3 rank. 

#### Patrons
Thanks to all the backers and sponsors! Support this project by <a href="https://www.patreon.com/glmn">becoming a patron</a>.