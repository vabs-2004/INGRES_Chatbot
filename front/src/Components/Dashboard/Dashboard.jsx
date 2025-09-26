import React from 'react'
import Section1 from './Section1'
import Section2 from './Section2'
import Section3 from './Section3'
import Section2A from './Section2A'
import './Dashboard.css'

const Dashboard = () => {
  return (
    <div className='dashboard'>
      <Section1/>
      <div className='section-2'>
        <Section2/>
        <Section2A/>
      </div>
      <Section3/>
    </div>
  )
}

export default Dashboard

// function Dashboard({ openChat }) {
//   return (
//     <div>
//       <h1>Dashboard</h1>
//       <button className="btn-primary" onClick={openChat}>
//         Chat with INGRES
//       </button>
//     </div>
//   );
// }

// export default Dashboard;
