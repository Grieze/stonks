import {useState, useEffect} from "react";
import Chart from "react-apexcharts";
import dayjs from "dayjs"

const URL = 'http://localhost:8000/';
const SERIES_ACCESS = 0;
// Has to make API call and get data from backend
const Charts = (formOptions) => {
    const [currentData, setCurrentData] = useState();
    const [currentOptions, setCurrentOptions] = useState({
        ticker : "NFLX",
        startDate : "2022-01-01",
        endDate : "2022-01-31",
        interval : "1d",
    })
    const getData = async () => {
        setCurrentOptions(formOptions);
        console.log(currentOptions);
        const response = await fetch(
            URL + `?ticker=${currentOptions.ticker}` + 
            `&start=${currentOptions.startDate}` + 
            `&end=${currentOptions.endDate}` + 
            `&interval=${currentOptions.interval}`
        );
        const data = await response.json();
        setCurrentData(data);
    };
    
    useEffect(() => {
        getData();
    }, []);

    useEffect(() => {
        setCurrentOptions(formOptions);
        console.log('currentOptions', currentOptions);
    });
    
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
          width: 300
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
              return dayjs(val).format('MM DD YY')
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
            width: 300
        },
        dataLabels: {
            enabled: false
        },
        xaxis: {
            categories : [],
            labels: {
                formatter: function(val) {
                    return dayjs(val).format('MM DD YY')
                }
            }
        },
        // TODO :
        /* Volume bars for periods when the close price > open price should be green. 
        Volume bars for periods when close price < open price should be red. 
        Volume bars for periods when open price = close price should be black.*/
        // colors : [],
    }
    
    for (let date in currentData) {
        candleSeries[SERIES_ACCESS].data.push({
            x : new Date(parseInt(date)),
            y : [currentData[date].Open, currentData[date].High, currentData[date].Low, currentData[date].Close]
        })
        barSeries[SERIES_ACCESS].data.push(currentData[date].Volume);
        barOptions.xaxis.categories.push(new Date(parseInt(date)));
        // barOptions.colors.push(() => {
        //     if (currentData[date].Close > currentData[date].Open) {
        //         return "#00b746";
        //     }
        //     else if (currentData[date].Close < currentData[date].Open) {
        //         return "#ef403c";
        //     }
        //     else {
        //         return "#000";
        //     } 
        // })
    }

    return (
        <div>
            <Chart options={candleOptions} series={candleSeries} type="candlestick" height={350}/>
            <Chart options={barOptions} series={barSeries} type="bar" height={200}/>
        </div>
    )
}

export default Charts;