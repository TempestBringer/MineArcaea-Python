# MineArcaea-Python

Minecraft : TempestZYTux
Bilibili : 海马络合物

将Arcaea谱面转换为包含连续执行的mcfunction的数据包以实现播放。

### 使用前环境准备：
将Arcaea解包后的文件按照如下目录结构放置，补全sum和songs文件夹即可。这些文件我不应该提供。

```text
|(项目文件夹)
|---- sum
        |---- packlist
        |---- songlist
|---- songs
        |---- aegleseeker
                |----0.aff
                |----1.aff
                |----2.aff
        |---- aiueoon
                |----0.aff
                |----1.aff
                |----2.aff
        |---- akinokagerou
                |----0.aff
                |----1.aff
                |----2.aff
        |---- (下略，总是就是很多以歌曲idx为名的文件夹)
|---- utils
        |---- arcs.py
        |---- file_reader.py
        |---- file_writer.py
        |---- hit_effect.py
        |---- render.py（没用，但是没删）
        |---- render_xp.py
|---- aff_convertor.py
|---- minearcaea.py
```
### 使用：
到minearcaea.py做一些参数调整，你会看到这两个参数，修改index为歌曲id，difficulty为谱面难度等级，你可以修改这两个参数转换不同谱面。

path为输出产生的数据包文件到哪里，最好事先创建这个目录，prefix代表生成mcfunction的前缀。
```text
index = 278
difficulty = 3
path = './pentiment'
prefix = 'pentiment'
```

到./utils/aff_convertor.py可以做更多的演出相关的参数调整。
最上方的 tps = 40 用于修改渲染的tps。在使用carpet变速的时候调到该tps以达到正常速度。

此外还有很多可以修改的参数，具体参考aff_convertor/get_args方法的注释。

修改好以后在minearcaea.py运行主函数即可，输出可以忽略。

### 使用提示：
1.更高的tps可以使演出结果更加流畅，但是会显著增加数据包大小，过高的tps甚至会使mc来不及渲染远处的方块变化（只是渲染，不影响运算）从而产生”一些note在远处卡着不动“的现象，请小心提升。同样显著影响数据包大小的参数还有黑线粒子密度'particle_dense'，这两者都是越低，体积越小。你也不想被上GB的数据包撑爆游戏运行时内存吧？

2.配置参数里有一些跟”打击效果“有关的参数，那些是最初想用粒子拼成判定图像的尝试，后来发现对数据包大小的增加有惊人的贡献，所以砍了，那些参数现在没用。

3.你需要自己搭建主要的演出轨道，该程序只会在4k->6k的时候渲染附加的轨道。

4.项目未经完备的测试，可能含有若干bug（笑死，根本不做try catch），但是在默认参数下转换testify和pentiment的beyond难度是没问题的。