def Number2Text(number : int):
    match number:
        case 1:
            return "最新消息"
        case 2:
            return "新聞稿"
        case 3:
            return "營運資訊"
        case 4:
            return "轉乘資訊"
        case 5:
            return "活動訊息"
        case 6:
            return "系統公告"
        case 7:
            return "新服務上架"
        case 8:
            return "API修正"
        case 9:
            return "來源異常"
        case 10:
            return "資料更新"
        case 99:
            return "其他"