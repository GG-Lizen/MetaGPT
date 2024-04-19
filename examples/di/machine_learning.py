import fire

from metagpt.roles.di.data_interpreter import DataInterpreter

WINE_REQ = "Run data analysis on sklearn Wine recognition dataset, include a plot, and train a model to predict wine class (20% as validation), and show validation accuracy."


train_path = "E:/MyTask/Metagpt/dataset/salesForecast/train.csv"
eval_path="E:/MyTask/Metagpt/dataset/salesForecast/eval.csv"
# sales_forecast data from https://www.kaggle.com/datasets/aslanahmedov/walmart-sales-forecast/data
SALES_FORECAST_REQ = f"""This dataset contains Walmart's historical sales data, including 'Store', 'Dept', 'Date', 'Weekly_Sales', and 'IsHoliday'. Your goal is to forecast 'Weekly_Sales' considering holiday effects. Perform data analysis by plotting sales trends, holiday effects, distribution of sales across stores/departments using box/violin plots, time series decomposition, heatmaps of sales across stores over time, correlation matrices between features, and error distribution of predictions. After modeling, compare actual vs. predicted sales through plots to assess accuracy. Use MAE or RMSE for evaluation. Ensure your analysis includes dynamic sales trends over time, especially around holidays, factor impact on sales via bar charts, and prediction error analysis. Train data path: {train_path}, Eval data path: {eval_path}.
"""
# SALES_FORECAST_REQ = f"""该数据集包含沃尔玛的历史销售数据，包括“Store”、“Dept”、“Date”、“Weekly_Sales”和“IsHoliday”。您的目标是考虑假日效应来预测“Weekly_Sales”。通过绘制销售趋势、假日效应、使用箱线图/小提琴图展示销售在各店铺/部门之间的分布、时间序列分解、随时间变化的店铺销售热图、特征之间的相关矩阵以及预测误差分布等进行数据分析。建模后，通过绘图比较实际销售与预测销售，以评估准确性。使用MAE或RMSE进行评估。确保您的分析包括随时间动态变化的销售趋势，特别是在假日周围，通过条形图展示因素对销售的影响，以及预测误差分析。训练数据路径：{train_path}，评估数据路径：{eval_path}。"""
REQUIREMENTS = {"wine": WINE_REQ, "sales_forecast": SALES_FORECAST_REQ}


REQUIREMENTS = {"wine": WINE_REQ, "sales_forecast": SALES_FORECAST_REQ}


async def main(use_case: str = "wine"):
    mi = DataInterpreter()
    requirement = REQUIREMENTS[use_case]
    await mi.run(requirement)


if __name__ == "__main__":
    fire.Fire(main)
