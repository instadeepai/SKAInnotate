import React from 'react';
import { Button, Modal, ModalActions, ModalContent, ModalHeader } from "semantic-ui-react"

const RoleSelectionModal = ({dispatchModal, modalState}) => {
  return (
    <Modal
      size="tiny"
      open={modalState.open}
      onClose={() => dispatchModal({ type: 'CLOSE_MODAL' })}
    >
    <ModalHeader>Select a Role</ModalHeader>
    <ModalContent>
        <p>You must select a role before accessing project.</p>
    </ModalContent>
      <ModalActions>
          <Button positive onClick={() => dispatchModal({ type: 'CLOSE_MODAL' })}>
            OK
          </Button>
        </ModalActions>
    </Modal>
  )
}

export default RoleSelectionModal;