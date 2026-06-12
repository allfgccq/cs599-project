from typing import Dict, Any, List


class ContentAgent:
    """特约导游 Agent - 调用知识库，生成景点深度攻略"""
    
    def __init__(self):
        self.attraction_guides = {
            "西湖": {
                "guide": "西湖是杭州的标志性景点，建议从断桥开始游览，沿着白堤漫步到苏堤，途中可以欣赏到三潭印月的美景。",
                "tips": ["最佳游览时间：清晨或傍晚", "建议游玩时间：3-4小时", "周边美食：楼外楼、知味观"],
                "history": "西湖自唐代起就成为著名的风景名胜，历经千年依然保持着迷人的景色。"
            },
            "灵隐寺": {
                "guide": "灵隐寺是江南著名古刹，始建于东晋咸和元年。进入景区后先游览飞来峰石窟造像，再进入寺庙参拜。",
                "tips": ["建议请讲解员", "门票包含飞来峰景区", "寺内素斋值得一试"],
                "history": "灵隐寺是杭州历史最悠久的佛教寺院，拥有1600多年历史。"
            },
            "故宫": {
                "guide": "故宫是明清两代的皇家宫殿，建议从午门进入，沿着中轴线游览三大殿，然后参观东西六宫。",
                "tips": ["建议提前网上购票", "最佳游览时间：上午", "建议租用讲解器"],
                "history": "故宫始建于明永乐年间，是世界上现存规模最大、保存最为完整的木质结构古建筑群。"
            },
            "八达岭长城": {
                "guide": "八达岭长城是万里长城的精华段，建议从北坡攀登，可以选择徒步或乘坐缆车。",
                "tips": ["建议穿舒适的运动鞋", "注意防晒", "下山可选择滑道"],
                "history": "八达岭长城始建于明朝，是长城中最著名的一段，也是游客最多的地方。"
            },
            "外滩": {
                "guide": "外滩是上海的标志性景观，建议晚上游览，可以欣赏到对岸陆家嘴的灯光秀。",
                "tips": ["最佳观赏时间：晚上", "建议从南京东路步行至外滩", "节假日人较多"],
                "history": "外滩是上海近代历史的见证，汇集了各国风格的建筑。"
            }
        }
    
    def generate_guide(self, attraction_name: str) -> Dict[str, Any]:
        """生成景点深度攻略"""
        guide = self.attraction_guides.get(attraction_name)
        
        if guide:
            return {
                "success": True,
                "data": {
                    "attraction": attraction_name,
                    "guide": guide["guide"],
                    "tips": guide["tips"],
                    "history": guide["history"],
                    "avoid_tips": self._get_avoid_tips(attraction_name)
                },
                "error": None
            }
        
        return {
            "success": False,
            "data": None,
            "error": {"code": "NOT_FOUND", "message": f"未找到 {attraction_name} 的攻略信息", "details": ""}
        }
    
    def _get_avoid_tips(self, attraction_name: str) -> List[str]:
        """获取避坑指南"""
        tips = {
            "西湖": ["节假日断桥人流量非常大，建议错峰游览", "湖边有很多付费拍照服务，注意价格"],
            "灵隐寺": ["景区门口有很多兜售香烛的小贩，寺内可以免费领取", "节假日停车困难，建议公共交通"],
            "故宫": ["周一闭馆，注意安排时间", "景区内餐饮价格较高，建议自带水和零食"],
            "八达岭长城": ["节假日缆车排队时间很长", "山上温差大，注意保暖"],
            "外滩": ["节假日灯光秀期间人非常多", "江边风大，注意添衣"]
        }
        return tips.get(attraction_name, [])