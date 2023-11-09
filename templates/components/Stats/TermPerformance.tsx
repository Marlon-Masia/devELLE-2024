import React from 'react'
import { Card, CardHeader, Collapse, Button, Modal, ModalHeader, ModalBody } from 'reactstrap';
import ClassPerformance from './ClassPerformance';
import SpecificStudentStats from './SpecificStudentStats';
import { ClassDetailsType } from '../Profile/AdminView';
import { useUser } from '@/hooks/useUser';

export default function TermPerformance({ classes }: { classes: ClassDetailsType[] }) {
    const [collapseTab, setCollapseTab] = React.useState(-1);
    const [modalOpen, setModalOpen] = React.useState(false);
    const [currentGroup, setCurrentGroup] = React.useState<string>("");

    const permission = useUser().user?.permission;

    const toggleTab = (e: React.MouseEvent<HTMLElement, MouseEvent>) => {
        let event = e.currentTarget.dataset.event; 
    
        //if the accordion clicked on is equal to the current accordion that's open then close the current accordion,
        //else open the accordion you just clicked on 
        // this.setState({ collapseTab: this.state.collapseTab === Number(event) ? -1 : Number(event) })
        setCollapseTab(collapseTab === Number(event) ? -1 : Number(event));
    }

    const toggleModal = (id: string) => {
        // this.setState({ modalOpen: !this.state.modalOpen, currentGroup: id });
        setModalOpen(!modalOpen);
        setCurrentGroup(id);
    }

        return (
            <Card style={{backgroundColor: "#04354b", color: "aqua", overflow: "scroll", height: "45vh", borderTopLeftRadius: "0px"}}>
                {classes.map((group, i) => {
                    return (
                        <Card key={i} style={{border: "none", color: "black", borderRadius: "0px"}}>
                            <CardHeader style={{backgroundColor: "#74b7bd", color: "white", borderRadius: "0px", padding: "5px 20px"}} 
                                onClick={e => toggleTab(e)} data-event={i}>
                                {group.groupName}
                                {collapseTab === i && permission === "pf"?
                                <Button 
                                    style={{float: "right", padding: "2px 4px", fontSize: "small"}}
                                    onClick={() => toggleModal(group.groupID)}
                                >
                                    Lookup Student
                                </Button> 
                                : null}
                            </CardHeader>
                            
                            <Collapse isOpen={collapseTab === i} style={{border: "none"}}>
                                <ClassPerformance groupID={group.groupID}/>
                            </Collapse>
                        </Card>
                    )
                })}

                <Modal isOpen={modalOpen} toggle={() => setModalOpen(!modalOpen)}>
                    <ModalHeader toggle={() => setModalOpen(!modalOpen)}>Lookup Student</ModalHeader>
                    <ModalBody>
                        <SpecificStudentStats groupID={currentGroup}/>
                    </ModalBody>
                </Modal>
            </Card>
        );
}