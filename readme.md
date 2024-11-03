## 程序规划

```bash
# 程序层级
.
├── tool.exe
└── files
    ├── events.log
    ├── process.json
    ├── case.py
    ├── tool.db
    ├── videos
    │   └── xx.mp4
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
       1. 指定流程中的步骤片段执行
       2. 指定执行次数
    5. 保存流程: 将执行流程配置保存出来
    6. 读取流程:
       1. 指定流程文件读取
- [ ] 逆行生成流程py代码
    1. 根据流程生成py代码
    1. 指定文件目录输出
- [ ] 系统参数配置
    1. 将settings.py/ conf.py配置录入至数据库中
    2. 可指定修改

### 辅助功能

- [ ] 操作监控
    1. 记录操作
    2. 方法回溯

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

+ 监控记录（records)

  | 字段名      | 字段类型 | 备注     | 示例值                                                       |
    | ----------- | -------- | -------- | ------------------------------------------------------------ |
  | id          | int      | 监控编号 | 1                                                            |
  | event       | str      | 事件内容 | ['click', 'left', true,  x, y]<br>or<br> ['scroll', x, y, dx, dy] |
  | image_name  | str      | 事件图   | md5名字                                                      |
  | record_time | str      | 触发时间 | 2001.1.1 0:0:0                                               |

+ 配置(confs)

  | 字段名        | 字段类型 | 备注    | 示例值    |
    |------------|------|-------|--------|
  | id         | int  | 键值编号  | 1      |
  | keys       | str  | 键名    | BORDER |
  | values     | str  | 值     | 100    |
  | decipt_key | str  | 键名描述  | 边界     |
  | required   | int  | 是否为必须 | 1      |

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
