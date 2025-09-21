import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ETFAnalyzer:
    """ETF分析器"""
    
    def __init__(self, tushare_client):
        """
        初始化ETF分析器
        
        Args:
            tushare_client: Tushare客户端实例
        """
        self.tushare_client = tushare_client
    
    def get_etf_info(self, etf_code: str) -> Optional[Dict]:
        """
        获取ETF基本信息
        
        Args:
            etf_code: ETF代码
            
        Returns:
            Dict: ETF基本信息
        """
        try:
            basic_info = self.tushare_client.get_etf_basic_info(etf_code)
            if not basic_info:
                return None
            
            # 格式化基本信息
            etf_info = {
                'code': etf_code,
                'name': basic_info.get('name', ''),
                'management': basic_info.get('management', ''),
                'current_price': basic_info.get('current_price', 0),
                'pre_close': basic_info.get('pre_close', 0),
                'pct_change': basic_info.get('pct_change', 0),
                'volume': basic_info.get('volume', 0),
                'amount': basic_info.get('amount', 0),
                'trade_date': basic_info.get('trade_date', ''),
                'found_date': basic_info.get('found_date', ''),
                'list_date': basic_info.get('list_date', ''),
                'data_age_days': basic_info.get('data_age_days', 0)  # 数据新鲜度
            }
            
            return etf_info
            
        except Exception as e:
            logger.error(f"获取ETF {etf_code} 信息失败: {str(e)}")
            return None
    
    def get_historical_data(self, etf_code: str, days: int = 90) -> Optional[pd.DataFrame]:
        """
        获取ETF历史数据
        
        Args:
            etf_code: ETF代码
            days: 历史天数
            
        Returns:
            DataFrame: 历史数据
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 获取历史数据
            df = self.tushare_client.get_etf_daily_data(
                etf_code=etf_code,
                start_date=start_date.strftime('%Y%m%d'),
                end_date=end_date.strftime('%Y%m%d')
            )
            
            return df
            
        except Exception as e:
            logger.error(f"获取ETF {etf_code} 历史数据失败: {str(e)}")
            return None
    
    def analyze_etf_characteristics(self, historical_data: pd.DataFrame) -> Dict:
        """
        分析ETF特征
        
        Args:
            historical_data: 历史数据DataFrame
            
        Returns:
            Dict: 分析结果
        """
        try:
            if historical_data.empty or len(historical_data) < 20:
                return {
                    'error': '数据不足，无法进行分析',
                    'data_points': len(historical_data)
                }
            
            # 基础统计
            close_prices = historical_data['close'].values
            volumes = historical_data['vol'].values
            amplitudes = historical_data['amplitude'].values
            
            # 价格分析
            current_price = float(close_prices[-1])
            avg_price = float(np.mean(close_prices))
            price_std = float(np.std(close_prices))
            price_range = float(np.max(close_prices) - np.min(close_prices))
            
            # 波动率分析
            daily_returns = np.diff(close_prices) / close_prices[:-1]
            volatility = float(np.std(daily_returns) * np.sqrt(252) * 100)  # 年化波动率
            
            # 振幅分析
            avg_amplitude = float(np.mean(amplitudes))
            max_amplitude = float(np.max(amplitudes))
            min_amplitude = float(np.min(amplitudes))
            amplitude_std = float(np.std(amplitudes))
            
            # 成交量分析
            avg_volume = float(np.mean(volumes))
            volume_std = float(np.std(volumes))
            
            # 趋势分析
            trend_slope = self._calculate_trend_slope(close_prices)
            trend_direction = self._determine_trend_direction(trend_slope)
            
            # 震荡特征分析
            oscillation_score = self._calculate_oscillation_score(
                close_prices, amplitudes
            )
            
            # 流动性分析
            liquidity_score = self._calculate_liquidity_score(volumes, avg_volume)
            
            # 价格分布分析
            price_distribution = self._analyze_price_distribution(close_prices)
            
            # 获取实际数据日期范围
            start_date = historical_data['trade_date'].min().strftime('%Y-%m-%d')
            end_date = historical_data['trade_date'].max().strftime('%Y-%m-%d')
            
            analysis_result = {
                # 基础信息
                'current_price': current_price,
                'avg_price': avg_price,
                'price_std': price_std,
                'price_range': price_range,
                
                # 波动率信息
                'volatility': volatility,
                'volatility_level': self._classify_volatility(volatility),
                
                # 振幅信息
                'avg_amplitude': avg_amplitude,
                'max_amplitude': max_amplitude,
                'min_amplitude': min_amplitude,
                'amplitude_std': amplitude_std,
                'amplitude_level': self._classify_amplitude(avg_amplitude),
                
                # 成交量信息
                'avg_volume': avg_volume,
                'volume_std': volume_std,
                'liquidity_score': liquidity_score,
                
                # 趋势信息
                'trend_slope': trend_slope,
                'trend_direction': trend_direction,
                
                # 震荡特征
                'oscillation_score': oscillation_score,
                'market_character': self._classify_market_character(oscillation_score, trend_direction),
                
                # 价格分布
                'price_distribution': price_distribution,
                
                # 数据质量
                'data_points': len(historical_data),
                'start_date': start_date,
                'end_date': end_date,
                'analysis_date': datetime.now().isoformat()
            }
            
            logger.info("ETF特征分析完成")
            return analysis_result
            
        except Exception as e:
            logger.error(f"分析ETF特征失败: {str(e)}")
            return {'error': f'分析失败: {str(e)}'}
    
    def evaluate_adaptability(self, analysis_result: Dict, grid_params: Dict, user_frequency: str = 'medium') -> Dict:
        """
        评估ETF对网格交易的适应性
        
        Args:
            analysis_result: 分析结果
            grid_params: 网格参数
            user_frequency: 用户期望频率 ('high', 'medium', 'low')
            
        Returns:
            Dict: 适应性评估结果
        """
        try:
            if 'error' in analysis_result:
                return {
                    'is_suitable': False,
                    'reason': analysis_result['error'],
                    'score': 0,
                    'dimension_scores': {
                        'amplitude_score': 0,
                        'volatility_score': 0,
                        'market_score': 0,
                        'liquidity_score': 0,
                        'grid_params_score': 0
                    }
                }
            
            score = 0
            reasons = []
            warnings = []
            
            # 记录各维度得分
            dimension_scores = {
                'amplitude_score': 0,
                'volatility_score': 0,
                'market_score': 0,
                'liquidity_score': 0,
                'grid_params_score': 0
            }
            
            # 1. 振幅评估 (30分)
            avg_amplitude = analysis_result.get('avg_amplitude', 0)
            if avg_amplitude >= 2.0:
                dimension_scores['amplitude_score'] = 30
                score += 30
            elif avg_amplitude >= 1.5:
                dimension_scores['amplitude_score'] = 20
                score += 20
                warnings.append("日均振幅偏低，可能影响网格收益")
            else:
                dimension_scores['amplitude_score'] = 0
                reasons.append("日均振幅过小，难以覆盖交易成本")
            
            # 2. 波动率评估 (25分)
            volatility = analysis_result.get('volatility', 0)
            if 15 <= volatility <= 40:
                dimension_scores['volatility_score'] = 25
                score += 25
            elif volatility < 15:
                dimension_scores['volatility_score'] = 15
                score += 15
                warnings.append("波动率偏低，网格交易机会较少")
            else:
                dimension_scores['volatility_score'] = 10
                score += 10
                warnings.append("波动率过高，风险较大")
            
            # 3. 市场特征评估 (20分)
            market_character = analysis_result.get('market_character', '')
            oscillation_score = analysis_result.get('oscillation_score', 0)
            
            if market_character == '震荡':
                dimension_scores['market_score'] = 20
                score += 20
            elif market_character == '弱趋势':
                dimension_scores['market_score'] = 15
                score += 15
            elif market_character == '强趋势':
                dimension_scores['market_score'] = 5
                score += 5
                reasons.append("市场趋势性较强，不适合网格交易")
            else:
                dimension_scores['market_score'] = 0
            
            # 4. 流动性评估 (15分)
            liquidity_score = analysis_result.get('liquidity_score', 0)
            avg_volume = analysis_result.get('avg_volume', 0)
            
            if liquidity_score >= 0.7 and avg_volume >= 1000000:  # 100万股
                dimension_scores['liquidity_score'] = 15
                score += 15
            elif liquidity_score >= 0.5 and avg_volume >= 500000:
                dimension_scores['liquidity_score'] = 10
                score += 10
                warnings.append("流动性一般，需注意交易冲击成本")
            else:
                dimension_scores['liquidity_score'] = 0
                reasons.append("流动性不足，可能存在交易风险")
            
            # 5. 网格参数合理性评估 (10分) - 新的动态评估逻辑
            grid_params_evaluation = self._evaluate_grid_params_with_frequency_matching(
                analysis_result, grid_params, user_frequency
            )
            dimension_scores['grid_params_score'] = grid_params_evaluation['total_score']
            score += grid_params_evaluation['total_score']
            
            # 添加网格参数相关的警告和建议
            if grid_params_evaluation['total_score'] < 8:
                warnings.extend(grid_params_evaluation['warnings'])
            
            # 综合评估
            is_suitable = score >= 60 and len(reasons) == 0
            
            return {
                'is_suitable': is_suitable,
                'score': score,
                'max_score': 100,
                'dimension_scores': dimension_scores,
                'grid_params_details': grid_params_evaluation,  # 新增：网格参数详细评估
                'reasons': reasons,
                'warnings': warnings,
                'recommendation': self._generate_recommendation(is_suitable, score, reasons, warnings)
            }
            
        except Exception as e:
            logger.error(f"适应性评估失败: {str(e)}")
            return {
                'is_suitable': False,
                'reason': f'评估失败: {str(e)}',
                'score': 0
            }
    
    def _calculate_trend_slope(self, prices: np.ndarray) -> float:
        """计算价格趋势斜率"""
        try:
            x = np.arange(len(prices))
            slope, _ = np.polyfit(x, prices, 1)
            return float(slope)
        except:
            return 0.0
    
    def _determine_trend_direction(self, slope: float) -> str:
        """判断趋势方向"""
        if slope > 0.01:
            return '上涨趋势'
        elif slope < -0.01:
            return '下跌趋势'
        else:
            return '震荡'
    
    def _calculate_oscillation_score(self, prices: np.ndarray, amplitudes: np.ndarray) -> float:
        """计算震荡特征分数"""
        try:
            # 价格标准差与均值比
            price_cv = np.std(prices) / np.mean(prices)
            
            # 振幅变异系数
            amplitude_cv = np.std(amplitudes) / np.mean(amplitudes)
            
            # 综合震荡分数 (0-1)
            oscillation_score = min(1.0, (price_cv * 10 + amplitude_cv) / 2)
            
            return float(oscillation_score)
        except:
            return 0.0
    
    def _calculate_liquidity_score(self, volumes: np.ndarray, avg_volume: float) -> float:
        """计算流动性分数"""
        try:
            # 成交量稳定性
            volume_cv = np.std(volumes) / np.mean(volumes)
            
            # 平均成交量充足性
            volume_adequacy = min(1.0, avg_volume / 1000000)  # 以100万股为基准
            
            # 综合流动性分数
            liquidity_score = (1 - min(1.0, volume_cv)) * 0.5 + volume_adequacy * 0.5
            
            return float(liquidity_score)
        except:
            return 0.0
    
    def _analyze_price_distribution(self, prices: np.ndarray) -> Dict:
        """分析价格分布特征"""
        try:
            # 计算分位数
            q25, q50, q75 = np.percentile(prices, [25, 50, 75])
            
            # 计算偏度和峰度（使用scipy.stats）
            from scipy import stats
            skewness = float(stats.skew(prices))
            kurtosis = float(stats.kurtosis(prices))
            
            return {
                'q25': float(q25),
                'q50': float(q50),
                'q75': float(q75),
                'iqr': float(q75 - q25),
                'skewness': skewness,
                'kurtosis': kurtosis,
                'distribution_type': self._classify_distribution(skewness, kurtosis)
            }
        except Exception as e:
            logger.error(f"价格分布分析失败: {str(e)}")
            return {
                'q25': 0.0,
                'q50': 0.0,
                'q75': 0.0,
                'iqr': 0.0,
                'skewness': 0.0,
                'kurtosis': 0.0,
                'distribution_type': '无法分析'
            }
    
    def _classify_volatility(self, volatility: float) -> str:
        """分类波动率水平"""
        if volatility < 10:
            return '低波动'
        elif volatility < 25:
            return '中等波动'
        elif volatility < 40:
            return '高波动'
        else:
            return '极高波动'
    
    def _classify_amplitude(self, avg_amplitude: float) -> str:
        """分类振幅水平"""
        if avg_amplitude < 1.0:
            return '极小振幅'
        elif avg_amplitude < 1.5:
            return '小振幅'
        elif avg_amplitude < 2.5:
            return '中等振幅'
        elif avg_amplitude < 4.0:
            return '大振幅'
        else:
            return '极大振幅'
    
    def _classify_market_character(self, oscillation_score: float, trend_direction: str) -> str:
        """分类市场特征"""
        if oscillation_score > 0.6:
            return '震荡'
        elif oscillation_score > 0.3:
            return '弱趋势'
        else:
            return '强趋势'
    
    def _classify_distribution(self, skewness: float, kurtosis: float) -> str:
        """分类价格分布类型"""
        if abs(skewness) < 0.5 and abs(kurtosis) < 0.5:
            return '正态分布'
        elif skewness > 0.5:
            return '右偏分布'
        elif skewness < -0.5:
            return '左偏分布'
        else:
            return '其他分布'
    
    def _evaluate_grid_params_with_frequency_matching(self, analysis_result: Dict, 
                                                    grid_params: Dict, 
                                                    user_frequency: str) -> Dict:
        """
        基于用户频率期望的动态网格参数评估
        
        Args:
            analysis_result: ETF分析结果
            grid_params: 网格参数
            user_frequency: 用户期望频率
            
        Returns:
            Dict: 网格参数评估结果
        """
        try:
            # 用户期望的日交易频次
            target_daily_frequencies = {
                'high': 5.5,    # 高频：5-6次/天
                'medium': 2.5,  # 中频：2-3次/天
                'low': 1.0      # 低频：1次/天
            }
            
            target_triggers = target_daily_frequencies.get(user_frequency, 2.5)
            avg_amplitude = analysis_result.get('avg_amplitude', 0.02)
            
            # 1. 动态计算合理的价格区间范围
            optimal_range = self._calculate_optimal_price_range(avg_amplitude, target_triggers)
            
            # 2. 动态计算合理的网格数量范围
            optimal_grid_count = self._calculate_optimal_grid_count(
                user_frequency, target_triggers, optimal_range['base_range'], avg_amplitude
            )
            
            # 3. 评估实际参数
            actual_range = grid_params.get('price_range_ratio', 0)
            actual_count = grid_params.get('grid_count', 0)
            
            # 4. 价格区间评分 (5分)
            range_score = self._score_price_range(actual_range, optimal_range)
            
            # 5. 网格数量评分 (5分)
            count_score = self._score_grid_count(actual_count, optimal_grid_count)
            
            # 6. 频次匹配度奖励 (最多2分额外奖励)
            frequency_match_score = grid_params.get('frequency_match_score', 0)
            bonus_score = 0
            if frequency_match_score > 0.8:
                bonus_score = 2
            elif frequency_match_score > 0.6:
                bonus_score = 1
            
            total_score = min(10, range_score + count_score + bonus_score)
            
            # 7. 生成警告和建议
            warnings = []
            suggestions = []
            
            if range_score < 3:
                if actual_range < optimal_range['min_range']:
                    warnings.append(f"价格区间过小({actual_range:.1%})，建议调整至{optimal_range['min_range']:.1%}-{optimal_range['max_range']:.1%}")
                else:
                    warnings.append(f"价格区间过大({actual_range:.1%})，建议调整至{optimal_range['min_range']:.1%}-{optimal_range['max_range']:.1%}")
            
            if count_score < 3:
                if actual_count < optimal_grid_count['min_count']:
                    warnings.append(f"网格数量过少({actual_count}个)，建议调整至{optimal_grid_count['min_count']}-{optimal_grid_count['max_count']}个")
                else:
                    warnings.append(f"网格数量过多({actual_count}个)，建议调整至{optimal_grid_count['min_count']}-{optimal_grid_count['max_count']}个")
            
            if frequency_match_score < 0.6:
                warnings.append(f"当前参数预计触发频率与期望不符，匹配度仅{frequency_match_score:.1%}")
            
            return {
                'total_score': total_score,
                'range_evaluation': {
                    'score': range_score,
                    'actual': actual_range,
                    'optimal': optimal_range,
                    'status': 'good' if range_score >= 4 else 'needs_adjustment'
                },
                'count_evaluation': {
                    'score': count_score,
                    'actual': actual_count,
                    'optimal': optimal_grid_count,
                    'status': 'good' if count_score >= 4 else 'needs_adjustment'
                },
                'frequency_matching': {
                    'target_triggers': target_triggers,
                    'predicted_triggers': grid_params.get('predicted_daily_triggers', 0),
                    'match_score': frequency_match_score,
                    'bonus_score': bonus_score
                },
                'warnings': warnings,
                'suggestions': suggestions
            }
            
        except Exception as e:
            logger.error(f"网格参数评估失败: {str(e)}")
            return {
                'total_score': 0,
                'warnings': [f'参数评估失败: {str(e)}'],
                'suggestions': []
            }
    
    def _calculate_optimal_price_range(self, avg_amplitude: float, target_triggers: float) -> Dict:
        """计算最优价格区间"""
        try:
            # 基础公式：区间 = 振幅 × 频率系数 × 安全边际
            frequency_multiplier = target_triggers * 1.2  # 频率系数
            safety_margin = 1.5  # 安全边际
            
            base_range = avg_amplitude * frequency_multiplier * safety_margin
            
            # 应用约束条件
            min_range = max(0.02, base_range * 0.8)   # 最小2%，考虑交易成本
            max_range = min(0.50, base_range * 1.3)   # 最大50%，风险控制
            
            # 确保min_range < max_range
            if min_range >= max_range:
                min_range = max_range * 0.8
            
            return {
                'base_range': base_range,
                'min_range': min_range,
                'max_range': max_range,
                'calculation_basis': f'振幅{avg_amplitude:.1%} × 频率系数{frequency_multiplier:.1f} × 安全边际{safety_margin}'
            }
            
        except Exception as e:
            logger.error(f"计算最优价格区间失败: {str(e)}")
            return {
                'base_range': 0.15,
                'min_range': 0.10,
                'max_range': 0.25,
                'calculation_basis': '使用默认值'
            }
    
    def _calculate_optimal_grid_count(self, frequency_type: str, target_triggers: float, 
                                    base_range: float, avg_amplitude: float) -> Dict:
        """计算最优网格数量"""
        try:
            # 基于频率类型的基础网格数
            if frequency_type == 'high':
                base_count = int(base_range / (avg_amplitude / target_triggers))
                min_count = max(12, base_count - 5)
                max_count = min(30, base_count + 8)
            elif frequency_type == 'medium':
                base_count = int(base_range / (avg_amplitude / target_triggers))
                min_count = max(6, base_count - 3)
                max_count = min(18, base_count + 5)
            else:  # low
                base_count = int(base_range / (avg_amplitude / target_triggers))
                min_count = max(3, base_count - 2)
                max_count = min(10, base_count + 3)
            
            # 确保合理性
            if min_count >= max_count:
                max_count = min_count + 3
            
            return {
                'base_count': base_count,
                'min_count': min_count,
                'max_count': max_count,
                'frequency_type': frequency_type
            }
            
        except Exception as e:
            logger.error(f"计算最优网格数量失败: {str(e)}")
            # 默认值
            default_ranges = {
                'high': {'min_count': 12, 'max_count': 25},
                'medium': {'min_count': 6, 'max_count': 15},
                'low': {'min_count': 3, 'max_count': 8}
            }
            default = default_ranges.get(frequency_type, default_ranges['medium'])
            return {
                'base_count': (default['min_count'] + default['max_count']) // 2,
                'min_count': default['min_count'],
                'max_count': default['max_count'],
                'frequency_type': frequency_type
            }
    
    def _score_price_range(self, actual_range: float, optimal_range: Dict) -> int:
        """评分价格区间设置"""
        try:
            min_range = optimal_range['min_range']
            max_range = optimal_range['max_range']
            
            if min_range <= actual_range <= max_range:
                return 5  # 完美匹配
            
            # 计算偏离程度
            optimal_center = (min_range + max_range) / 2
            deviation = abs(actual_range - optimal_center) / optimal_center
            
            if deviation < 0.2:  # 偏离20%以内
                return 4
            elif deviation < 0.4:  # 偏离40%以内
                return 3
            elif deviation < 0.6:  # 偏离60%以内
                return 2
            elif deviation < 1.0:  # 偏离100%以内
                return 1
            else:
                return 0
                
        except:
            return 2  # 默认中等分数
    
    def _score_grid_count(self, actual_count: int, optimal_count: Dict) -> int:
        """评分网格数量设置"""
        try:
            min_count = optimal_count['min_count']
            max_count = optimal_count['max_count']
            
            if min_count <= actual_count <= max_count:
                return 5  # 完美匹配
            
            # 计算偏离程度
            optimal_center = (min_count + max_count) / 2
            deviation = abs(actual_count - optimal_center) / optimal_center
            
            if deviation < 0.2:  # 偏离20%以内
                return 4
            elif deviation < 0.4:  # 偏离40%以内
                return 3
            elif deviation < 0.6:  # 偏离60%以内
                return 2
            elif deviation < 1.0:  # 偏离100%以内
                return 1
            else:
                return 0
                
        except:
            return 2  # 默认中等分数

    def _generate_recommendation(self, is_suitable: bool, score: int, 
                                reasons: List[str], warnings: List[str]) -> str:
        """生成推荐建议"""
        if is_suitable:
            recommendation = "✅ 该ETF适合进行网格交易"
            if warnings:
                recommendation += f"\n⚠️  注意事项：{'; '.join(warnings)}"
        else:
            recommendation = "❌ 该ETF不适合进行网格交易"
            if reasons:
                recommendation += f"\n📋 主要原因：{'; '.join(reasons)}"
            if warnings:
                recommendation += f"\n⚠️  其他风险：{'; '.join(warnings)}"
        
        recommendation += f"\n📊 综合评分：{score}/100"
        
        return recommendation
