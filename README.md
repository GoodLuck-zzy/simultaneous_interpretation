# simultaneous_interpretation
demo
192.168.33.71
```
conda activate smlss_server
pip install -i  https://pypi.mirrors.ustc.edu.cn/simple/ -r requirements.txt
cd backend
python3 -m commands.init_database
python3 run.py
 nohup python3 run.py --port 15000 > logs/output.log 2>&1 &

```