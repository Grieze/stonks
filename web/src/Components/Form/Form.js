import {useState, useEffect} from 'react'
import { useForm } from 'react-hook-form'
import Charts from '../Charts/Charts';

// https://remotestack.io/how-to-create-radio-buttons-in-using-react-hook-form/

export default function Form() {
  const [options, setOptions] = useState({});
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm()

  const onSubmit = (data) => {
    setOptions(data)
    console.log(options)
  }

  return (
    <div>
      <form id="textInputs">
      </form>
      <form onSubmit={handleSubmit(onSubmit)}>
        
        <label>
        Ticker:
        <input 
        {...register('ticker', { required: true })}
        type="text" name="ticker" id="ticker"/>{' '}
        </label>

        <label>
        Start Date:
        <input 
        {...register('startDate', { required: true })}
        type="date" name="startDate" id="startDate" />{' '}
        </label>

        <label>
        End Date:
        <input 
        {...register('endDate', { required: true })}
        type="date" name="endDate" id="endDate" />{' '}
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
              id="daily"
            />{' '}
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
              id="weekly"
            />{' '}
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
              id="monthly"
            />{' '}
            Monthly
          </label>
        </div>

        <div className="text-danger mt-2">
          {errors.interval?.type === 'required' && 'Value is required'}
        </div>

        <button type="submit" className="btn btn-primary mt-3">
          Submit
        </button>
      </form>
      < Charts formOptions={options}/>
    </div>
  )
}