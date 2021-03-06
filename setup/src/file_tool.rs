#![allow(dead_code)]
#![allow(unused_imports)]
#![allow(unused_variables)]
#![allow(unknown_lints)]


//For File Struct
use std::fs;
use std::fs::{read_dir, metadata};

//For read to string
use std::io::prelude::*;

//For exists
use std::path::Path;

//For get current dir
use std::env;

use std::time::{SystemTime, Duration};
use std::io::Result;

pub struct File {
    pub path: String,
}
impl File {
    pub fn new(path: String) -> Self {
        File {
            path,
        }
    }

    // Returns content of file
    pub fn read(&self) -> String {
        let mut file = fs::File::open(&self.path).expect("File could not be opened");
        let mut contents = String::new();
        file.read_to_string(&mut contents).expect("Import failed");
        return contents;
    }

    // Overwrites file with content
    pub fn write(&self, content: String) -> bool {
        let mut file = fs::File::create(&self.path).unwrap();
        file.write_all(content.as_bytes()).unwrap();
        drop(file);
        true
    }

    pub fn file_exists(&self) -> bool {
        let path = Path::new(&self.path);
        path.exists() && path.is_file()
    }


    pub fn dir_exists(&self) -> bool {
        let path = Path::new(&self.path);
        path.exists() && path.is_dir()
    }

    /// 获取文件最后修改时间
    pub fn file_modify_time(&self) -> Option<u64> {
        let path = Path::new(&self.path);
        if let Ok(fs) = metadata(path) {
            if let Ok(time) = fs.modified() {
                if let Ok(now) = SystemTime::now().duration_since(time) {
                    return Some(now.as_secs());
                }
            }
        }
        return None;
    }

    pub fn ls(&self) -> Vec<String> {
        let paths = fs::read_dir(self.path.clone()).unwrap();
        let mut files: Vec<String> = vec![];
        for path in paths {
            if let Ok(path) = path {
                if let Some(path) = path.path().to_str() {
                    files.push(path.to_string());
                }
            }
        }
        files
    }

    pub fn rm(&self) -> bool {
        let path = Path::new(&self.path);
        if self.dir_exists() {
            if let Ok(_) = fs::remove_dir_all(self.path.clone()) {
                return true;
            }
        }
        else if self.file_exists() {
            if let Ok(_) = fs::remove_file(self.path.clone()) {
                return true;
            }
        }
        false
    }
}

/// 获取当前运行文件夹
pub fn cur_dir() -> String {
    let path = env::current_dir()
        .ok()
        .expect("Failed get current dir");
    return path.display().to_string()
}