let xData = ['2025年\n7月', '2025年\n9月', '2025年\n9月', '2025年\n10月', '2025年\n11月', '2025年\n12月']
let yData = [200, 189, 234,156, 298, 231]
const colors = []
// 最小值展示不同颜色
let minNumber = Math.min(...yData)
yData.forEach((item) => {
   if (item == minNumber) {
      colors.push({
         left: 'rgba(234, 162, 57, .16)',
         right: 'rgba(234, 162, 57, .6)',
         top: 'rgba(234, 162, 57, 1)',
         bottom: 'rgba(234, 162, 57, .46)',
         front: 'rgba(234, 162, 57, .66)',
      })
   } else {
      colors.push({
         left: 'rgba(45, 179, 255, .16)',
         right: 'rgba(45, 179, 255, .6)',
         top: 'rgba(45, 179, 255, 1)',
         bottom: 'rgba(45, 179, 255, .46)',
         front: 'rgba(45, 179, 255, .66)',
      })
   }
})

// 注册5个面图形:左侧、前面、右面、上面、下面
//c0:左下角，c1：右下角,c2:右上角，c3：左上角
// 绘制左侧面-ok rgba(103, 180, 233, 0.04)
const CubeLeft_1 = echarts.graphic.extendShape({
   shape: {
      x: 0,
      y: 0,
   },
   buildPath: function (ctx, shape) {
      // 会canvas的应该都能看得懂，shape是从custom传入的
      const xAxisPoint = shape.xAxisPoint
      const c0 = [shape.x - 20, shape.y]
      const c1 = [shape.x - 2, shape.y - 14]
      const c2 = [xAxisPoint[0] - 2, xAxisPoint[1] - 14]
      const c3 = [xAxisPoint[0] - 20, xAxisPoint[1]]
      ctx.moveTo(c0[0], c0[1]).lineTo(c1[0], c1[1]).lineTo(c2[0], c2[1]).lineTo(c3[0], c3[1]).closePath()
   },
})
const CubeFront_1 = echarts.graphic.extendShape({
   shape: {
      x: 0,
      y: 0,
   },
   buildPath: function (ctx, shape) {
      // 会canvas的应该都能看得懂，shape是从custom传入的
      const xAxisPoint = shape.xAxisPoint
      const c0 = [shape.x - 20, shape.y]
      const c1 = [shape.x + 18, shape.y]
      const c2 = [xAxisPoint[0] + 18, xAxisPoint[1]]
      const c3 = [xAxisPoint[0] - 20, xAxisPoint[1]]
      ctx.moveTo(c0[0], c0[1]).lineTo(c1[0], c1[1]).lineTo(c2[0], c2[1]).lineTo(c3[0], c3[1]).closePath()
   },
})
const CubeRight_1 = echarts.graphic.extendShape({
   shape: {
      x: 0,
      y: 0,
   },
   buildPath: function (ctx, shape) {
      const xAxisPoint = shape.xAxisPoint
      const c0 = [shape.x + 18, shape.y]
      const c1 = [shape.x + 36, shape.y - 14]
      const c2 = [xAxisPoint[0] + 36, xAxisPoint[1] - 14]
      const c3 = [xAxisPoint[0] + 18, xAxisPoint[1]]
      ctx.moveTo(c0[0], c0[1]).lineTo(c1[0], c1[1]).lineTo(c2[0], c2[1]).lineTo(c3[0], c3[1]).closePath()
   },
})
const CubeTop_1 = echarts.graphic.extendShape({
   shape: {
      x: 0,
      y: 0,
   },
   buildPath: function (ctx, shape) {
      const c0 = [shape.x - 20, shape.y]
      const c1 = [shape.x + 18, shape.y]
      const c2 = [shape.x + 36, shape.y - 14]
      const c3 = [shape.x - 2, shape.y - 14]
      ctx.moveTo(c0[0], c0[1]).lineTo(c1[0], c1[1]).lineTo(c2[0], c2[1]).lineTo(c3[0], c3[1]).closePath()
   },
})
const CubeBottom_1 = echarts.graphic.extendShape({
   shape: {
      x: 0,
      y: 0,
   },
   buildPath: function (ctx, shape) {
      // 会canvas的应该都能看得懂，shape是从custom传入的
      const xAxisPoint = shape.xAxisPoint

      const c0 = [xAxisPoint[0] - 20, xAxisPoint[1]]
      const c1 = [xAxisPoint[0] + 18, xAxisPoint[1]]
      const c2 = [xAxisPoint[0] + 36, xAxisPoint[1] - 14]
      const c3 = [xAxisPoint[0] - 2, xAxisPoint[1] - 14]

      ctx.moveTo(c0[0], c0[1]).lineTo(c1[0], c1[1]).lineTo(c2[0], c2[1]).lineTo(c3[0], c3[1]).closePath()
   },
})

echarts.graphic.registerShape('CubeLeft_1', CubeLeft_1)
echarts.graphic.registerShape('CubeFront_1', CubeFront_1)
echarts.graphic.registerShape('CubeRight_1', CubeRight_1)
echarts.graphic.registerShape('CubeTop_1', CubeTop_1)
echarts.graphic.registerShape('CubeBottom_1', CubeBottom_1)
option = {
   backgroundColor:"#102E44",
   tooltip: {
      trigger: 'axis',
      formatter: '{b}: {c} 万度',
      axisPointer: { type: 'shadow' },
   },
   grid: {
      left: '5%',
      right: '6%',
      top: '37%',
      bottom: '20%',
      containLabel: true,
   },
   xAxis: {
      type: 'category',
      data: xData,
      offset: 10,

      axisTick: {
         show: false,
      },
      axisLabel: {
         show: true,
         color: '#fff',
         fontSize: 14,
         align: 'center',
      },
      axisLine: {
         show: true,
         lineStyle: {
            color: 'rgba(186, 231, 255, 0.65)',
         },
      },
   },
   yAxis: {
      // interval: 20,
      type: 'value',
      name: '万度',
      nameTextStyle: {
         color: 'rgba(230, 247, 255, 0.65)',
         // fontSize: "14px",
         align: 'center',
         padding: [0, 28, 4, 0],
      },
      alignTicks: true,
      axisLine: {
         show: false,
         lineStyle: {
            color: 'rgba(255, 255, 255, .16)',
         },
      },
      splitLine: {
         show: true,
         lineStyle: {
            type: 'dashed',
            color: 'rgba(230, 247, 255, 0.2)',
         },
      },
      axisTick: {
         show: false,
      },
      axisLabel: {
         show: true,
         fontSize: 16,
         color: 'rgba(230, 247, 255, 0.65)',
      },
   },
   series: [
      {
         type: 'custom',
         renderItem: (params, api) => {
            const location = api.coord([api.value(0), api.value(1)])
            var color =
               api.value(1) > 10000
                  ? 'red'
                  : new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                     {
                        offset: 0,
                        color: '#5cc4eb',
                     },
                     {
                        offset: 0.8,
                        color: '#21658c',
                     },
                  ])
            return {
               type: 'group',
               children: [
                  {
                     type: 'CubeBottom_1',
                     shape: {
                        api,
                        xValue: api.value(0),
                        yValue: api.value(1),
                        x: location[0],
                        y: location[1],
                        xAxisPoint: api.coord([api.value(0), 0]),
                     },
                     style: {
                        fill: colors[params.dataIndexInside]['bottom'],
                     },
                  },
                  {
                     type: 'CubeLeft_1',
                     shape: {
                        api,
                        xValue: api.value(0),
                        yValue: api.value(1),
                        x: location[0],
                        y: location[1],
                        xAxisPoint: api.coord([api.value(0), 0]),
                     },
                     style: {
                        fill: colors[params.dataIndexInside]['left'],
                     },
                  },
                  {
                     type: 'CubeFront_1',
                     shape: {
                        api,
                        xValue: api.value(0),
                        yValue: api.value(1),
                        x: location[0],
                        y: location[1],
                        xAxisPoint: api.coord([api.value(0), 0]),
                     },
                     style: {
                        fill: colors[params.dataIndexInside]['front'],
                     },
                  },
                  {
                     type: 'CubeRight_1',
                     shape: {
                        api,
                        xValue: api.value(0),
                        yValue: api.value(1),
                        x: location[0],
                        y: location[1],
                        xAxisPoint: api.coord([api.value(0), 0]),
                     },
                     style: {
                        fill: colors[params.dataIndexInside]['right'],
                     },
                  },
                  {
                     type: 'CubeTop_1',
                     shape: {
                        api,
                        xValue: api.value(0),
                        yValue: api.value(1),
                        x: location[0],
                        y: location[1],
                        xAxisPoint: api.coord([api.value(0), 0]),
                     },
                     style: {
                        fill: colors[params.dataIndexInside]['top'],
                     },
                  },
               ],
            }
         },
         data: yData,
      },
      {
         type: 'bar',
         barWidth: 20,
         label: {
            show: true,
            position: 'top',
            // formatter: (e) => {
            //    return e.value + '%'
            // },
            formatter: function (i) {
               console.log(i)
               if (i.value == minNumber) {
                  return '{a|' + i.value + '}'
               } else {
                  return '{b|' + i.value + '}'
               }
            },
            rich: {
               a: {
                  color: '#FF6B01',
                  fontSize: 12,
                  fontWeight: 700,
                  align: 'center',
               },
               b: {
                  color: '#31BFFD',
                  fontSize: 12,
                  fontWeight: 700,
                  align: 'center',
               },
            },
            fontSize: 12,
            fontWeight: 700,
            // color: '#31BFFD',
            offset: [10, -15, 0, 0],
         },
         itemStyle: {
            color: 'transparent',
         },
         data: yData,
      },
   ],
};
