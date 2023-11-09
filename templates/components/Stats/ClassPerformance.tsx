import React, { useCallback, useEffect } from 'react';
import { Card, Row, Col } from 'reactstrap';
import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';
import axios from 'axios';
import TermStats from './TermStats';
import TermBarChart from './TermBarChart';

export type TermStatsType = {
    termID: string;
    front: string;
    back: string;
    correctness: number;
    count: number;
    modules: string[];
};

export default function ClassPerformance({ groupID }: { groupID: string }) {
    const [termStats, setTermStats] = React.useState<TermStatsType[]>([]);
    const [error, setError] = React.useState<string>('');
    const [threshold, setThreshold] = React.useState(50);

    const getTermsPerformance = useCallback(() => {
        let header = {
            headers: { Authorization: 'Bearer ' + localStorage.getItem('jwt') },
            params: { groupID },
        };

        axios
            .get('elleapi/termsperformance', header)
            .then((res) => {
                setTermStats(res.data);
            })
            .catch((error) => {
                setError(error.response);
                console.log(error.response);
            });
    }, [groupID]);

    useEffect(() => {
        getTermsPerformance();
    }, [getTermsPerformance]);

    const renderCharts = () => {
        return (
            <Row style={{ margin: '0px' }}>
                <Col xs="7" style={{ padding: '0px' }}>
                    <Card
                        style={{
                            height: '35vh',
                            borderRadius: '0px',
                            border: 'none',
                            overflow: 'scroll',
                        }}
                    >
                        <TermStats termStats={termStats} />
                    </Card>
                </Col>
                <Col xs="5" style={{ padding: '0px' }}>
                    <Card
                        style={{
                            height: '35vh',
                            borderRadius: '0px',
                            borderRightStyle: 'hidden',
                        }}
                    >
                        <TermBarChart
                            termStats={termStats}
                            threshold={threshold}
                        />
                        <Slider
                            value={threshold}
                            style={{ width: '80%', margin: '5px 30px' }}
                            onChange={changeThreshold}
                        />
                        <p
                            style={{
                                textAlign: 'end',
                                padding: '0px 30px',
                                fontSize: '10px',
                            }}
                        >
                            Threshold: {threshold}%
                        </p>
                    </Card>
                </Col>
            </Row>
        );
    };

    const changeThreshold = (value: number | number[]) => {
        if (typeof value === 'number') setThreshold(value);
        else setThreshold(value[0]);
    };

    return error ? (
        <p style={{ margin: '10px 15px' }}>No records found.</p>
    ) : (
        renderCharts()
    );
}