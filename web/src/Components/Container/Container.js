import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import dayjs from "dayjs"
import Chart from "react-apexcharts";

const URL = 'http://localhost:8000/';
const CANDLE_SERIES_ACCESS = 0;
const GREEN = "#00b746";
const RED = "#ef403c";
const BLACK = "#000"
const Container = () => {
  const [currentStockData, setCurrentStockData] = useState();
  const [currentOptions, setCurrentOptions] = useState({
    ticker : "",
    startDate : "",
    endDate : "",
    interval : "",
  });
  const getData = async () => {
    const response = await fetch(
    URL + 
    `?ticker=${currentOptions.ticker}` + 
    `&start=${currentOptions.startDate}` + 
    `&end=${currentOptions.endDate}` + 
    `&interval=${currentOptions.interval}`
    );
    const data = await response.json();
    setCurrentStockData(data);
  };
    
  useEffect(() => {
    console.log(currentOptions) 
    getData();
  }, [currentOptions]);

  const {
      register,
      handleSubmit,
      formState: { errors },
  } = useForm()

  const onSubmit = (data) => {
    setCurrentOptions(data);
  }

  const candleSeries = [{
      name : 'OHLC',
      data : []
  }];

  const barSeries = [{
      name : 'Daily Trading Volume',
      data : []
  }]

  const candleOptions = {
      chart: {
        height: 200,
        type: 'candlestick',
        width: 400
      },
      title: {
        align: 'center'
      },
      tooltip: {
        enabled: true,
      },
      xaxis: {
        labels: {
          formatter: function(val) {
            return dayjs(val).format('MM/DD/YYYY')
          }
        }
      },
      yaxis: {
        tooltip: {
          enabled: true
        }
      }
  };
  
  const barOptions = {
      chart: {
          height: 200,
          type: 'bar',
          width: 400
      },
      dataLabels: {
          enabled: false
      },
      plotOptions: {
        bar: {
          distributed: true, // this line is mandatory
          horizontal: false,
          barheight: '85%',
        }
      },
      xaxis: {
          categories : [],
          labels: {
              formatter: function(val) {
                  return dayjs(val).format('MM/DD/YYYY')
              }
          }
      },
      fill : {
        opacity: 1,
      },
      legend: {
        show: false,
      },
      // TODO : fix volume bars
      colors : [],
  }
  
  for (let date in currentStockData) {
    candleSeries[CANDLE_SERIES_ACCESS].data.push({
      // multiply by 1000 to convert from epoch to microseconds time
      x : new Date(parseInt(date)),
      y : [currentStockData[date].Open, currentStockData[date].High, currentStockData[date].Low, currentStockData[date].Close]
    })
    barSeries[CANDLE_SERIES_ACCESS].data.push(currentStockData[date].Volume);
    barOptions.xaxis.categories.push(new Date(parseInt(date)));
    if (currentStockData[date].Close > currentStockData[date].Open) {
      barOptions.colors.push(GREEN);
    }
    else if (currentStockData[date].Close < currentStockData[date].Open) {
      barOptions.colors.push(RED);
    }
    else {
      barOptions.colors.push(BLACK);
    }
  }
  // console.log(barOptions.colors);

  return (
  <div className="Container">
    {/* <form id="textInputs"></form> */}
    <form>
      <label>
      Ticker:
      <input 
      {...register('ticker', { required: true })}
      type="text" name="ticker" id="ticker"/>
      </label>
      <label>
      Start Date:
      <input 
      {...register('startDate', { required: true })}
      type="date" name="startDate" id="startDate" />
      </label>
      <label>
      End Date:
      <input 
      {...register('endDate', { required: true })}
      type="date" name="endDate" id="endDate" />
      </label>
      <p>Choose your interval</p>
      <div className="form-check">
        <label htmlFor="daily">
          <input
          {...register('interval', { required: true })}
          type="radio"
          name="interval"
          value="1d"
          className="form-check-input"
          id="daily"/>
          Daily
        </label>
      </div>
      <div className="form-check">
        <label htmlFor="weekly">
          <input
          {...register('interval', { required: true })}
          type="radio"
          name="interval"
          value="1wk"
          className="form-check-input"
          id="weekly"/>
          Weekly
        </label>
      </div>
      <div className="form-check">
        <label htmlFor="monthly">
          <input
          {...register('interval', { required: true })}
          type="radio"
          name="interval"
          value="1mo"
          className="form-check-input"
          id="monthly"/>
          Monthly
        </label>
      </div>
      <div className="text-danger mt-2">{errors.interval?.type === 'required' && 'Value is required'}</div>
      <button type="submit" className="btn btn-primary mt-3" onClick={handleSubmit(onSubmit)}>
        Submit
      </button>
    </form>
    <Chart options={candleOptions} series={candleSeries} type="candlestick" height={450}/>
    <Chart options={barOptions} series={barSeries} type="bar" height={200}/>
  </div>
)}

export default Container;