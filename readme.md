## 程序规划
```bash
# 程序层级
.
├── tool.exe
└── files
    ├── events.log
    ├── process.json
    ├── case.py
    ├── log
    │   └── 2001-1-1.log
    └── image
        └── md5.png
```



### 主功能

- [ ] 可视化流程式执行方法函数
  1. 新增步骤: 搜索方法并弹出对应方法参数配置
  2. 删除步骤: 选中存在步骤进行删除
  3. 重置: 清空流程
  4. 执行: 按照缓存步骤进行执行
  5. 保存流程: 将执行流程配置保存出来
- [ ] 逆行生成流程py代码
  1. 根据流程生成py代码
### 辅助功能
- [ ] 操作监控
  1. 记录操作
  2. 方法回溯
- [ ] CPU GPU RAM信息监控


## 数据
### 表设计

+ 功能表(functions)

  | 字段名        | 字段类型 | 备注                | 示例值        |
  | ------------- | -------- | ------------------- | ------------- |
  | id            | int      | 方法编号            | 1             |
  | func          | str      | 方法名              | set_value     |
  | params        | str      | 参数 json字符串     | {'value': 1}  |
  | depict_func   | str      | 方法描述            | 设置值        |
  | depict_params | str      | 参数描述 json字符串 | {'value': 值} |
  | depict_return | str      | 返回值描述          | None          |

+ 热键(hotkeys)

  | 字段名        | 字段类型 | 备注                         | 示例值               |
  | ------------- | -------- | ---------------------------- | -------------------- |
  | id            | int      | 热键组合编号                 | 1                    |
  | hotkey        | str      | 热键                         | ctrl, c              |
  | depict_hotkey | str      | 热键描述                     | 复制                 |
  | index_func    | str      | 索引方法，绑定               | copy \| null         |
  | index_params  | str      | 索引方法入参(通常为默认参数) | {'value': 1} \| null |

+ 监控记录（records)

  | 字段名      | 字段类型 | 备注     | 示例值                                                       |
  | ----------- | -------- | -------- | ------------------------------------------------------------ |
  | id          | int      | 监控编号 | 1                                                            |
  | event       | str      | 事件内容 | ['click', 'left', true,  x, y]<br>or<br> ['scroll', x, y, dx, dy] |
  | image_name  | str      | 事件图   | md5名字                                                      |
  | record_time | str      | 触发时间 | 2001.1.1 0:0:0                                               |

+ 配置(confs)

  | 字段名     | 字段类型 | 备注     | 示例值 |
  | ---------- | -------- | -------- | ------ |
  | id         | int      | 键值编号 | 1      |
  | keys       | str      | 键名     | BORDER |
  | values     | str      | 值       | 100    |
  | decipt_key | str      | 键名描述 | 边界   |

  

### 临时数据文件

+ 操作监控中的信息(events.log) 

  > 从触发监控开始录制到结束

  信息格式: time, [event]

+ 执行流程文件(process.json)

  > 默认流程配置格式

  ```json
  [
      {
          "func": "set_value",
          "params": {
              "value": 1
          }
      },
      {
          "func": "set_value",
          "params": {
              "value": 2
          }
      }
  ]
  ```

+ 流程py代码生成(case.py)

  > 目标： 生成allure，pytest的用例的py文件

+ 图片存储(image/md5.png)

  > 操作监控产生的图
