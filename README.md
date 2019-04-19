# Overlay Router

## Projects
### ovrouterd: the daemon
### ovrouter-graphql: the northbound API
### setup
### tinc-plugin


## 
### Prerequisites:
    tinc:
        liblzo2-2
    ovrouterd:
        libcurl4-openssl-dev
        
### debug
    cargo run --bin ovrouter -- -d 2

### run
    Only support ubuntu 16.04
    需要在运行目录有Settings.toml文件，或者修改settings.rs，Settings.toml文件地址
    `
    cp ./Settings.toml.example ./Settings.toml
    cargo build --release
    ./ovrouter -d 2
    `
## Todo
   
   ### Ovroute web server 
        []. uid检查(未确定Conductor发送格式)
        []. get check pub_key 返回http格式未确认
        []. 响应Conductor发送的添加hosts请求，
            []. 未确定Conductor发送格式
            []. 添加tinc hosts文件，在tinc operater中添加了add_hosts(未与Conductor调试)
