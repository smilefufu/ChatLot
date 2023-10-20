"""各种prompt模板"""

MONTH_ATTENDANCE = """CREATE TABLE dw_月度考勤表 (
    group_name text,
    userid text,
    用户名 text,
    mm_time text,
    dd_time timestamp without time zone,
    出勤天数 double precision,
    出差时长 double precision,
    旷工天数 double precision,
    加班总时长 double precision,
    上午 text,
    下午 text,
    dept_b character varying(64),
    dept_c character varying(64),
    调休总时长 double precision,
    病假总时长 double precision,
    事假总时长 double precision,
    其他假总时长 double precision,
    加班_审批单统计 double precision,
    应出勤天数 bigint,
    计薪日 double precision
);
表里每一行存储的是员工每天的打卡情况，用户名是员工的名字，dd_time是日期，出勤天数是当日累计出勤天数减去各种假期后的合计值
group_name是该员工所属分组；dept_b是员工所在的大部门；而dept_c是大部门下的小部门，dept_c有可能为NULL；计薪日是指本月该员工按多少天计薪。"""

MONTH_ATTENDANCE_PROMPT = """数据库建表语句如下:
""" + MONTH_ATTENDANCE + """
请依据上述数据表结构及字段，字段类型以及表之间的关系，结合问题，回答我两个项目：1.该结果适合用什么echart来展示，给出echart的config；2.生成获取该结果的sql，并且给出使用该sql得到的查询结果字段和echart配置的对应关系。结果以json方式返回，不要做额外的解释。问题：
{}
"""

# 手术操作
_MED_COLUMN_OP = """手术操作名称
手术部位
手术存在状态
手术术式
手术入路
手术设备
医嘱下达时间
手术开始时间
手术结束时间
手术操作持续时间
手术日期
手术性质
手术等级
术中出血量
输血存在状态
术中输血成分
术中输血量
手术切口等级
手术切口愈合等级
麻醉方式
缺血类型
缺血时长
介入治疗日期
介入治疗名称
介入治疗手段
介入治疗用药
手术相关症状/诊断
手术相关症状/诊断存在状态
消融手段
引导方式
组织机构名称
手术优先级规则时间
文书记录时间"""

# 病理检查
_MED_COLUMN_CHECK = """`
标本部位（主体）
标本名称
标本获取方式
标本类型
病理诊断部位
病理诊断
病理诊断存在状态
病理分级名称
病理分级结果
病理分型名称
病理分型结果
病理分化程度
病理组织学类型
病理诊断占比
诊断名称
诊断名称存在状态
复发/转移
复发/转移存在状态
复发/转移部位
病程特点
严重程度
病理结构名称
病理结构占病灶比例
病灶临近结构
病灶临近结构关系
距临近结构距离
距离单位
是否见癌细胞
镜下癌细胞定量
评估项目名称
评估定序结果
病灶描述
病灶存在状态
病灶方位-诊断方位
病灶部位
病灶数量
病灶大小
病灶大小单位
浸润成分
浸润成分占比
病灶外形描述
侵润深度
病理HPV类型
HPV结果
切缘结果
切缘方位
切缘与肿瘤的距离（单位：mm）
标本采集时间
标本接收时间
病理申请时间
病理检查时间
病理报告时间
医嘱下达时间
组织机构名称
文书记录时间
`"""

# 淋巴结病理
_MED_COLUMN_LB = """`
淋巴结清扫部位（主体）
淋巴结清扫个数
淋巴结清扫总计数
淋巴结清扫阳性数量
淋巴结清扫阳性总计数
淋巴结清扫时间
淋巴结转移类型
组织机构名称
文书记录时间
`"""

# 药品表
_MED_COLUMN_MED = """`
活性成分
通用名
商品名
药品分类
药品方案
药物存在状态
治疗开始时间
治疗结束时间
医嘱下达时间
医嘱开始时间
医嘱结束时间
治疗时长
药物治疗周期数
药物单次剂量
药物单次剂量单位
给药途径
给药频率
药物剂型
药物相关症状/诊断
药物相关症状/诊断存在状态
药物相关症状/诊断时间
治疗目的
治疗线数
组织机构名称
文书记录时间
基因名称
基因名称存在状态
基因检测标本类型
检测方法
检测抗体名称
外显子
位点
基因检测定量方法
定性结果
`"""

# 分子病理+免疫组化
_MED_COLUMN_IMMU = """`
基因名称
基因名称存在状态
基因检测标本类型
检测方法
检测抗体名称
外显子
位点
基因检测定量方法
定性结果
定量结果
基因强度结果
突变类型
突变状态
分子病理申请时间
分子病理检查时间
分子病理报告时间
医嘱下达时间
组织机构名称
文书记录时间
`"""

MED_COLUMNS = {
    "手术操作": _MED_COLUMN_OP,
    "病理检查": _MED_COLUMN_CHECK,
    "淋巴结病理": _MED_COLUMN_LB,
    "药品表": _MED_COLUMN_MED,
    "分子病理和免疫组化": _MED_COLUMN_IMMU
}

# default prompt
MED_PROMPT = """{question}
根据以上病历信息中，对于{group_name}相关的
{columns}
这些字段，区分出有在病历中有提及的字段，并对其总结。将有总结出内容或提取到实体词的字段及结果以json格式返回。不必加其他解释或描述性内容。
"""

surgery_columns = "、".join(_MED_COLUMN_OP.split("\n"))
MED_PROMPT_SURGERY = """病历：`{question}`
该病历信息描述了{surg}共{len_surg}个手术。分别对每个手术进行"""+surgery_columns+"""这些字段的分析，然后进行实体词提取。未知字段或提取不到有效实体词的字段不要回答。手术相关症状/诊断及其存在状态要做一一对应。以json列表的格式回答。让我们一步一步来思考
"""

MED_PROMPT_SURGERY_DISTINCT = """病历：`{question}`
该病历中一共描述了{surg}共{len_surg}个手术，原病历中其对应描述分别都有哪些？以json列表回答，json要包含`手术名称`和`描述`两个字段。注意描述文本要和原文保持一致。"""

MED_PROMPT_SURGERY2 = """描述：`{text}`
分析上述关于手术{surgery_name}的描述，先判断`"""+surgery_columns+"""`这些字段要求中，哪些字段在描述有相关内容，然后针对这些有相关内容的字段进行总结和实体词提取，无相关内容的字段不要回答。`手术相关症状/诊断`和`手术相关症状/诊断存在状态`的内容需要一一对应。以json的格式回答。"""

medicine_column = "、".join(_MED_COLUMN_MED.split("\n"))
MED_PROMPT_MEDICINE_PRE = """病历：`{question}`
附录：
""" + medicine_column + """
逐字分析上述病历。每当有一个药品名被提及时，则记录一次该药品名。以json格式回答。
让我们一步一步思考
"""
